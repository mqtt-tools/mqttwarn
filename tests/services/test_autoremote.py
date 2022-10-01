# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


def test_autoremote_success(srv, mocker, caplog):

    item = Item(
        target="test",
        addrs=["ApiKey", "Password", "Target", "Group", "TTL"],
        topic="autoremote/user",
        message="⚽ Notification message ⚽",
    )

    module = load_module_from_file("mqttwarn/services/autoremote.py")

    requests_mock = mocker.patch("requests.get")

    outcome = module.plugin(srv, item)
    requests_mock.assert_called_once_with(
        "https://autoremotejoaomgcd.appspot.com/sendmessage",
        params={
            "key": "ApiKey",
            "message": "⚽ Notification message ⚽",
            "target": "Target",
            "sender": "autoremote/user",
            "password": "Password",
            "ttl": "TTL",
            "collapseKey": "Group",
        },
    )

    assert outcome is True
    assert "Sending to autoremote service" in caplog.messages
    assert "Successfully sent to autoremote service" in caplog.messages


def test_autoremote_failure(srv, mocker, caplog):

    item = Item(
        target="test",
        addrs=["ApiKey", "Password", "Target", "Group", "TTL"],
        topic="autoremote/user",
        message="⚽ Notification message ⚽",
    )

    module = load_module_from_file("mqttwarn/services/autoremote.py")

    requests_mock = mocker.patch("requests.get", side_effect=Exception("something failed"))

    outcome = module.plugin(srv, item)
    requests_mock.assert_called_once()

    assert outcome is False
    assert "Sending to autoremote service" in caplog.messages
    assert "Failed to send message to autoremote service: something failed" in caplog.messages
