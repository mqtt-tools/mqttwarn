# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


def test_alexa_notify_me_success(srv, mocker, caplog):

    module = load_module_from_file("mqttwarn/services/alexa-notify-me.py")

    accessCode = "myToken"
    item = Item(addrs=[accessCode], message="⚽ Notification message ⚽")

    requests_mock = mocker.patch("requests.post")
    outcome = module.plugin(srv, item)
    requests_mock.assert_called_once_with(
        url="https://api.notifymyecho.com/v1/NotifyMe",
        data='{"notification": "\\u26bd Notification message \\u26bd", "accessCode": "myToken"}',
    )

    assert outcome is True
    assert "Sending to NotifyMe service" in caplog.messages
    assert "Successfully sent to NotifyMe service" in caplog.messages


def test_alexa_notify_me_real_auth_failure(srv, caplog):
    module = load_module_from_file("mqttwarn/services/alexa-notify-me.py")

    accessCode = "myToken"
    item = Item(addrs=[accessCode], message="⚽ Notification message ⚽")

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Sending to NotifyMe service" in caplog.messages
    assert "Failed to send message to NotifyMe service" in caplog.text
