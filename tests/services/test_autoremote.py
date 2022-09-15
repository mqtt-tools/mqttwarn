# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


def test_autoremote_success(srv, caplog):

    item = Item(
        target="test",
        addrs=["ApiKey", "Password", "Target", "Group", "TTL"],
        topic="autoremote/user",
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/autoremote.py")

        with mock.patch("requests.get") as requests_mock:
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
        assert "Sending to autoremote service" in caplog.text
        assert "Successfully sent to autoremote service" in caplog.text


def test_autoremote_failure(srv, caplog):

    item = Item(
        target="test",
        addrs=["ApiKey", "Password", "Target", "Group", "TTL"],
        topic="autoremote/user",
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/autoremote.py")

        with mock.patch("requests.get", side_effect=Exception("something failed")) as requests_mock:
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

        assert outcome is False
        assert "Sending to autoremote service" in caplog.text
        assert "Failed to send message to autoremote service: something failed" in caplog.text
