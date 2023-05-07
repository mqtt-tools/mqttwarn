# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
import sys

import pytest

import mqttwarn.services.execute
from mqttwarn.model import ProcessorItem as Item


@pytest.mark.skipif(sys.platform == "win32", reason="This test does not work on Windows")
def test_execute_success(tmp_path, srv, caplog, capfd):
    """
    Dispatch a single command invocation, and verify it worked.
    """

    tmpfile = tmp_path / "spool.txt"
    tmpfile.write_text("Hello, world.")

    module = mqttwarn.services.execute

    item = Item(
        target="test",
        addrs=["cat", "[TEXT]"],
        message=str(tmpfile),
        data={},
    )

    outcome = module.plugin(srv, item)

    assert outcome is True
    stdout, stderr = capfd.readouterr()
    assert "Hello, world." == stdout


def test_execute_failure(srv, caplog, capfd):
    """
    Dispatch a single command invocation with an unknown command, and verify the failure will be logged.
    """

    module = mqttwarn.services.execute

    item = Item(
        target="test",
        addrs=["foobar"],
        message="",
        data={},
    )

    outcome = module.plugin(srv, item)

    assert outcome is False
    if sys.platform == "win32":
        assert "Cannot execute ['foobar'] because [WinError 2] The system cannot find the file specified" in caplog.text
    else:
        assert "Cannot execute ['foobar'] because [Errno 2] No such file or directory: 'foobar'" in caplog.text
