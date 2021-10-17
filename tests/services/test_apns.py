# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock
from unittest.mock import call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file
from surrogate import surrogate


@surrogate("apns")
@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_success(mock_apns_payload, mock_apns, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apns.py")

        cert_file, key_file = ["cert_file", "key_file"]
        item = Item(
            target="test",
            addrs=[cert_file, key_file],
            message="⚽ Notification message ⚽",
            data={"apns_token": "foobar", "payload": "{}"},
        )

        outcome = module.plugin(srv, item)

        assert mock_apns_payload.mock_calls == [
            call(
                alert="⚽ Notification message ⚽",
                custom={},
                sound="default",
                badge=1,
            ),
        ]
        assert mock_apns.mock_calls == [
            mock.call(use_sandbox=False, cert_file="cert_file", key_file="key_file"),
            call().gateway_server.send_notification("foobar", mock.ANY),
        ]

        assert outcome is True
        assert "Successfully published APNS notification to foobar" in caplog.text


@surrogate("apns")
@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_success_no_payload(mock_apns_payload, mock_apns, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apns.py")

        cert_file, key_file = ["cert_file", "key_file"]
        item = Item(
            target="test",
            addrs=[cert_file, key_file],
            message="⚽ Notification message ⚽",
            data={"apns_token": "foobar"},
        )

        outcome = module.plugin(srv, item)

        assert mock_apns_payload.mock_calls == [
            call(
                alert="⚽ Notification message ⚽",
                custom={},
                sound="default",
                badge=1,
            ),
        ]
        assert mock_apns.mock_calls == [
            mock.call(use_sandbox=False, cert_file="cert_file", key_file="key_file"),
            call().gateway_server.send_notification("foobar", mock.ANY),
        ]

        assert outcome is True
        assert "Successfully published APNS notification to foobar" in caplog.text


@surrogate("apns")
@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_success_custom_payload(mock_apns_payload, mock_apns, srv, caplog):

    with caplog.at_level(logging.DEBUG):

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

        assert mock_apns_payload.mock_calls == [
            call(
                alert="⚽ Notification message ⚽",
                custom={"baz": "qux"},
                sound="default",
                badge=1,
            ),
        ]
        assert mock_apns.mock_calls == [
            mock.call(use_sandbox=False, cert_file="cert_file", key_file="key_file"),
            call().gateway_server.send_notification("foobar", mock.ANY),
        ]

        assert outcome is True
        assert "Successfully published APNS notification to foobar" in caplog.text


@surrogate("apns")
@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_failure_invalid_config(mock_apns_payload, mock_apns, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apns.py")

        item = Item(
            target="test",
            addrs=[None],
            message="⚽ Notification message ⚽",
            data={"apns_token": "foobar", "payload": "{}"},
        )

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "Incorrect service configuration" in caplog.text


@surrogate("apns")
@mock.patch("apns.APNs", create=True)
@mock.patch("apns.Payload", create=True)
def test_apns_failure_apns_token_missing(mock_apns_payload, mock_apns, srv, caplog):

    with caplog.at_level(logging.DEBUG):

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
        assert "Cannot notify via APNS: apns_token is missing" in caplog.text
