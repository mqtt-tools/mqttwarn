# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
import os
import sys

import pytest

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_by_name

if os.getenv("GITHUB_ACTIONS") == "true" and sys.platform != "linux":
    raise pytest.skip(
        reason="On GHA, ntfy via Docker is only available on Linux",  # ty: ignore[unknown-argument, unused-ignore-comment, unused-ignore-comment]  # noqa: E501
        allow_module_level=True,
    )


@pytest.fixture
def item(ntfy_service):
    """
    Create notification item to process.
    """
    # Decode address of ntfy service API.
    ntfy_host, ntfy_port = ntfy_service

    return Item(
        addrs={"url": f"http://{ntfy_host}:{ntfy_port}/testdrive"},
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
        data={
            "priority": "high",
            "tags": "foo,bar,äöü",
            "click": "https://example.org/testdrive",
            "actions": "view, Adjust temperature 🌡, https://example.org/home-automation/temperature, body='{{\"temperature\": 18}}'",  # noqa: E501
        },
    )


def test_ntfy_plugin_integration_with_attachment(srv, caplog, attachment_dummy, item):
    """
    Test the whole plugin with a successful outcome.
    """

    # Load mqttwarn ntfy service module.
    module = load_module_by_name("mqttwarn.services.ntfy")

    # Modify notification item: Add an attachment.
    item.addrs["file"] = attachment_dummy.name

    outcome = module.plugin(srv, item)

    assert "Successfully sent message using ntfy" in caplog.messages
    assert outcome is True


def test_ntfy_plugin_integration_with_newline(srv, caplog, item):
    """
    Test the whole plugin with a successful outcome.
    """

    # Load mqttwarn ntfy service module.
    module = load_module_by_name("mqttwarn.services.ntfy")

    # Modify notification item: Use newline characters.
    item.message = "Some\nmore\ntext...\n" + item.message + "\nEven\nmore\ntext..."

    outcome = module.plugin(srv, item)

    assert "Successfully sent message using ntfy" in caplog.messages
    assert outcome is True


def test_ntfy_plugin_integration_with_attachment_and_newline(srv, caplog, attachment_dummy, item):
    """
    Test the whole plugin with a successful outcome.
    """

    # Load mqttwarn ntfy service module.
    module = load_module_by_name("mqttwarn.services.ntfy")

    # Modify notification item: Add an attachment _and_ use newline characters.
    item.addrs["file"] = attachment_dummy.name
    item.message = "Some\nmore\ntext...\n" + item.message + "\nEven\nmore\ntext..."

    outcome = module.plugin(srv, item)

    assert "Successfully sent message using ntfy" in caplog.messages
    assert outcome is True
