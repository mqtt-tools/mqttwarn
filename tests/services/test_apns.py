# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
from unittest import mock
from unittest.mock import call

import pytest

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file

pytest.skip(reason="The `apns` package is not ready for Python3", allow_module_level=True)


@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_success(mock_apns_payload, mock_apns, srv, caplog):

    module = load_module_from_file("mqttwarn/services/apns.py")

    cert_file, key_file = ["cert_file", "key_file"]
    item = Item(
        target="test",
        addrs=[cert_file, key_file],
        message="⚽ Notification message ⚽",
        data={"apns_token": "foobar", "payload": "{}"},
    )

    outcome = module.plugin(srv, item)

    assert mock_apns.mock_calls == [
        mock.call(use_sandbox=False, cert_file="cert_file", key_file="key_file"),
        call().gateway_server.send_notification("foobar", mock.ANY),
    ]
    assert mock_apns_payload.mock_calls == [
        call(
            alert="⚽ Notification message ⚽",
            custom={},
            sound="default",
            badge=1,
        ),
    ]

    assert outcome is True
    assert "Successfully published APNS notification to foobar" in caplog.messages


@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_success_no_payload(mock_apns_payload, mock_apns, srv, caplog):

    module = load_module_from_file("mqttwarn/services/apns.py")

    cert_file, key_file = ["cert_file", "key_file"]
    item = Item(
        target="test",
        addrs=[cert_file, key_file],
        message="⚽ Notification message ⚽",
        data={"apns_token": "foobar"},
    )

    outcome = module.plugin(srv, item)

    mock_apns.assert_called_once()
    mock_apns_payload.assert_called_once()

    assert outcome is True
    assert "Successfully published APNS notification to foobar" in caplog.messages


@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_success_custom_payload(mock_apns_payload, mock_apns, srv, caplog):

    module = load_module_from_file("mqttwarn/services/apns.py")

    cert_file, key_file = ["cert_file", "key_file"]
    item = Item(
        target="test",
        addrs=[cert_file, key_file],
        message="⚽ Notification message ⚽",
        data={
            "apns_token": "foobar",
            "payload": '{"custom": {"baz": "qux"}}',
        },
    )

    outcome = module.plugin(srv, item)

    mock_apns.assert_called_once()
    assert mock_apns_payload.mock_calls == [
        call(
            alert="⚽ Notification message ⚽",
            custom={"baz": "qux"},
            sound="default",
            badge=1,
        ),
    ]

    assert outcome is True
    assert "Successfully published APNS notification to foobar" in caplog.messages


@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_failure_invalid_config(mock_apns_payload, mock_apns, srv, caplog):

    module = load_module_from_file("mqttwarn/services/apns.py")

    item = Item(
        target="test",
        addrs=[None],
        message="⚽ Notification message ⚽",
        data={"apns_token": "foobar", "payload": "{}"},
    )

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Incorrect service configuration" in caplog.messages


@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_failure_apns_token_missing(mock_apns_payload, mock_apns, srv, caplog):

    module = load_module_from_file("mqttwarn/services/apns.py")

    cert_file, key_file = ["cert_file", "key_file"]
    item = Item(
        target="test",
        addrs=[cert_file, key_file],
        message="⚽ Notification message ⚽",
        data={},
    )

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Cannot notify via APNS: apns_token is missing" in caplog.messages
