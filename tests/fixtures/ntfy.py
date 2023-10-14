# -*- coding: utf-8 -*-
# Copyright (c) 2023 Andreas Motl <andreas.motl@panodata.org>
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
"""
Provide the `ntfy`_ API service as a session-scoped fixture to your test
harness.

Source: https://docs.ntfy.sh/install/#docker

.. _ntfy: https://ntfy.sh/
"""
import docker
import pytest
from pytest_docker_fixtures import images
from pytest_docker_fixtures.containers._base import BaseImage
from pytest_mqtt.util import probe_tcp_connect

images.settings["ntfy"] = {
    "image": "binwiederhier/ntfy",
    "version": "latest",
    "options": {
        "command": """
        serve
        --base-url="http://localhost:5555"
        --attachment-cache-dir="/tmp/ntfy-attachments"
        """,
        "publish_all_ports": False,
        "ports": {"80/tcp": "5555"},
    },
}


class Ntfy(BaseImage):

    name = "ntfy"

    def check(self):
        # TODO: Add real implementation.
        return True

    def pull_image(self):
        """
        Image needs to be pulled explicitly.
        Workaround against `404 Client Error: Not Found for url: http+docker://localhost/v1.23/containers/create`.

        - https://github.com/mqtt-tools/mqttwarn/pull/589#issuecomment-1249680740
        - https://github.com/docker/docker-py/issues/2101
        """
        docker_client = docker.from_env(version=self.docker_version)
        image_name = self.image
        docker_client.images.pull(image_name)

    def run(self):
        self.pull_image()
        super(Ntfy, self).run()


ntfy_image = Ntfy()


def is_ntfy_running() -> bool:
    return probe_tcp_connect("localhost", 5555)


@pytest.fixture(scope="session")
def ntfy_service():

    # Gracefully skip spinning up the Docker container if ntfy is already running.
    if is_ntfy_running():
        yield "localhost", 5555
        return

    ntfy_image.run()
    yield "localhost", 5555
    ntfy_image.stop()
