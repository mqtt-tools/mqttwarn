# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
import os

import pytest as pytest

import mqttwarn.services.file
from mqttwarn.model import ProcessorItem as Item


@pytest.mark.parametrize(
    "item",
    [
        Item(
            target="test",
            addrs=["/tmp/testdrive.log"],
            message="⚽ Notification message ⚽",
            data={},
        ),
        Item(
            target="test",
            addrs={"path": "/tmp/testdrive.log"},
            message="⚽ Notification message ⚽",
            data={},
        ),
    ],
    ids=["basic", "advanced"],
)
def test_file_success(fake_filesystem, srv, caplog, item):
    """
    Dispatch a single message and prove it is stored in the designated file.
    """

    module = mqttwarn.services.file
    outcome = module.plugin(srv, item)
    assert os.path.exists("/tmp/testdrive.log")

    assert outcome is True
    assert "Writing to file `/tmp/testdrive.log'" in caplog.messages
    assert open("/tmp/testdrive.log", mode="r", encoding="utf-8").read() == "\u26bd Notification message \u26bd"


def test_file_failure(fake_filesystem, srv, mocker, caplog):
    """
    When `io.open` fails, prove that the corresponding error code path is
    invoked.
    """

    item = Item(
        target="test",
        addrs=["/tmp/testdrive.log"],
        message="⚽ Notification message ⚽",
        data={},
    )

    module = mqttwarn.services.file

    mocker.patch("io.open", side_effect=Exception("something failed"))
    outcome = module.plugin(srv, item)
    assert not os.path.exists("/tmp/testdrive.log")

    assert outcome is False
    assert "Cannot write to file `/tmp/testdrive.log': something failed" in caplog.messages


@pytest.mark.parametrize(
    "item",
    [
        Item(
            target="test",
            addrs=["/tmp/testdrive.log"],
            message="⚽ Notification message ⚽",
            data={},
            config={"append_newline": True},
        ),
        Item(
            target="test",
            addrs={"path": "/tmp/testdrive.log", "append_newline": True},
            message="⚽ Notification message ⚽",
            data={},
        ),
    ],
    ids=["basic", "advanced"],
)
def test_file_append_newline_success(fake_filesystem, srv, caplog, item):
    """
    Dispatch **two** messages and prove they are **both** stored into the
    designated file, seperated by a newline character.
    """

    module = mqttwarn.services.file
    outcome1 = module.plugin(srv, item)
    outcome2 = module.plugin(srv, item)
    assert os.path.exists("/tmp/testdrive.log")

    assert outcome1 is True
    assert outcome2 is True
    assert "Writing to file `/tmp/testdrive.log'" in caplog.messages
    assert (
        open("/tmp/testdrive.log", mode="r", encoding="utf-8").read()
        == "\u26bd Notification message \u26bd\n\u26bd Notification message \u26bd\n"
    )


@pytest.mark.parametrize(
    "item",
    [
        Item(
            target="test",
            addrs=["/tmp/testdrive.log"],
            message="⚽ Notification message ⚽",
            data={},
            config={"overwrite": True},
        ),
        Item(
            target="test",
            addrs={"path": "/tmp/testdrive.log", "overwrite": True},
            message="⚽ Notification message ⚽",
            data={},
        ),
    ],
    ids=["basic", "advanced"],
)
def test_file_overwrite_success(fake_filesystem, srv, caplog, item):
    """
    Dispatch **two** messages and prove only **one** is stored into the
    designated file, because the service has been configured with
    `overwrite: True`.
    """

    module = mqttwarn.services.file
    outcome1 = module.plugin(srv, item)
    outcome2 = module.plugin(srv, item)
    assert os.path.exists("/tmp/testdrive.log")

    assert outcome1 is True
    assert outcome2 is True
    assert "Writing to file `/tmp/testdrive.log'" in caplog.messages
    assert open("/tmp/testdrive.log", mode="r", encoding="utf-8").read() == "\u26bd Notification message \u26bd"
