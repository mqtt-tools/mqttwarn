# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


def test_alexa_notify_me_success(srv, caplog):

    module = load_module_from_file("mqttwarn/services/alexa-notify-me.py")

    accessCode = "myToken"
    item = Item(addrs=[accessCode], message="⚽ Notification message ⚽")

    with caplog.at_level(logging.DEBUG):
        with mock.patch("requests.post") as requests_mock:
            outcome = module.plugin(srv, item)
            requests_mock.assert_called_once_with(
                url="https://api.notifymyecho.com/v1/NotifyMe",
                data='{"notification": "\\u26bd Notification message \\u26bd", "accessCode": "myToken"}',
            )

        assert outcome is True
        assert "Sending to NotifyMe service" in caplog.text
        assert "Successfully sent to NotifyMe service" in caplog.text


def test_alexa_notify_me_real_auth_failure(srv, caplog):
    module = load_module_from_file("mqttwarn/services/alexa-notify-me.py")

    accessCode = "myToken"
    item = Item(addrs=[accessCode], message="⚽ Notification message ⚽")

    with caplog.at_level(logging.DEBUG):
        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "Sending to NotifyMe service" in caplog.text
        assert "Failed to send message to NotifyMe service" in caplog.text
