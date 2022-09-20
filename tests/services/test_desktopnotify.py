# -*- coding: utf-8 -*-
# (c) 2022 The mqttwarn developers
import json
import logging
from unittest import mock
from unittest.mock import call

import pytest
from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import Struct, load_module_by_name
from surrogate import surrogate


@pytest.fixture
def desktop_notifier_mock(mocker):
    with surrogate("desktop_notifier"):
        notifier = mocker.patch("desktop_notifier.DesktopNotifier", create=True)
        mocker.patch("desktop_notifier.Urgency", create=True)
        mocker.patch("desktop_notifier.Button", create=True)
        mocker.patch("desktop_notifier.ReplyField", create=True)
        yield notifier


def test_desktopnotify_vanilla_success(desktop_notifier_mock, srv, caplog):

    module = load_module_by_name("mqttwarn.services.desktopnotify")

    item = Item(
        title="⚽ Notification title ⚽",
        message="⚽ Notification message ⚽",
    )

    # Plugin needs a real `Struct`.
    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):

        outcome = module.plugin(srv, item)

        assert desktop_notifier_mock.mock_calls == [
            call(),
            call().send_sync(message="⚽ Notification message ⚽", title="⚽ Notification title ⚽", sound=True),
        ]

        assert outcome is True
        assert "Sending desktop notification" in caplog.messages


def test_desktopnotify_vanilla_failure(desktop_notifier_mock, srv, caplog):

    module = load_module_by_name("mqttwarn.services.desktopnotify")

    item = Item(
        title="⚽ Notification title ⚽",
        message="⚽ Notification message ⚽",
    )

    # Plugin needs a real `Struct`.
    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):

        # Make the `send_sync` method fail.
        attrs = {"send_sync.side_effect": Exception("Something failed")}
        notifier_mock = mock.MagicMock(**attrs)
        module.notify = notifier_mock

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "Sending desktop notification" in caplog.messages
        assert "Invoking desktop notifier failed: Something failed" in caplog.messages


def test_desktopnotify_json_success(desktop_notifier_mock, srv, caplog):

    module = load_module_by_name("mqttwarn.services.desktopnotify")

    json_message = json.dumps(
        dict(
            title="⚽ Notification title ⚽",
            message="⚽ Notification message ⚽",
        )
    )

    item = Item(
        message=json_message,
    )

    # Plugin needs a real `Struct`.
    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):

        outcome = module.plugin(srv, item)

        assert desktop_notifier_mock.mock_calls == [
            call(),
            call().send_sync(message="⚽ Notification message ⚽", title="⚽ Notification title ⚽", sound=True),
        ]

        assert outcome is True
        assert "Sending desktop notification" in caplog.messages


def test_desktopnotify_no_sound_success(desktop_notifier_mock, srv, caplog):

    module = load_module_by_name("mqttwarn.services.desktopnotify")

    item = Item(
        title="⚽ Notification title ⚽",
        message="⚽ Notification message ⚽",
        config={"sound": False},
    )

    # Plugin needs a real `Struct`.
    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):

        outcome = module.plugin(srv, item)

        assert desktop_notifier_mock.mock_calls == [
            call(),
            call().send_sync(message="⚽ Notification message ⚽", title="⚽ Notification title ⚽", sound=False),
        ]

        assert outcome is True
        assert "Sending desktop notification" in caplog.messages
