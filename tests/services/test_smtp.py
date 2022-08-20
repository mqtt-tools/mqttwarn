# -*- coding: utf-8 -*-
# (c) 2022 The mqttwarn developers
import logging
import sys
from unittest import mock
from unittest.mock import call

import pytest
from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import Struct, load_module_from_file


@pytest.mark.skipif(sys.version_info < (3, 8), reason="This test only works on Python >= 3.8")
def test_smtp_plain(srv, caplog):
    """
    Pretend sending a plain text message with SMTP and verify API calls
    and message encoding matches the expectations.
    """

    module = load_module_from_file("mqttwarn/services/smtp.py")

    item = Item(
        config={
            "server": "localhost:25",
            "sender": "mqttwarn <mqttwarn@localhost>",
            "username": "foobar",
            "password": "bazqux",
            "starttls": True,
            "htmlmsg": False,
        },
        target="test",
        addrs=["foo@example.org", "bar@example.org"],
        message="Notification message",
    )

    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):
        with mock.patch("smtplib.SMTP", create=True) as smtplib_mock:
            outcome = module.plugin(srv, item)
            assert smtplib_mock.mock_calls == [
                call("localhost:25"),
                call().set_debuglevel(0),
                call().ehlo(),
                call().starttls(),
                call().login("foobar", "bazqux"),
                call().sendmail(
                    "mqttwarn <mqttwarn@localhost>",
                    ["foo@example.org", "bar@example.org"],
                    mock.ANY,
                ),
                call().quit(),
            ]

            # Specifically examine the email body.
            body = smtplib_mock.mock_calls[5].args[2]
            assert body.startswith('Content-Type: text/plain; charset="us-ascii"')
            assert "Content-Transfer-Encoding: 7bit" in body
            assert "Notification message" in body

        assert outcome is True
        assert (
            "Sending SMTP notification to test, addresses: ['foo@example.org', 'bar@example.org']"
            in caplog.text
        )
        assert "Successfully sent SMTP notification" in caplog.text


@pytest.mark.skipif(sys.version_info < (3, 8), reason="This test only works on Python >= 3.8")
def test_smtp_utf8(srv, caplog):
    """
    Pretend sending a UTF-8 message with SMTP and verify API calls
    and message encoding matches the expectations.
    """

    module = load_module_from_file("mqttwarn/services/smtp.py")

    item = Item(
        config={
            "server": "localhost:25",
            "sender": "mqttwarn <mqttwarn@localhost>",
            "username": "foobar",
            "password": "bazqux",
            "starttls": True,
            "htmlmsg": False,
        },
        target="test",
        addrs=["foo@example.org", "bar@example.org"],
        message="⚽ Notification message ⚽",
    )

    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):
        with mock.patch("smtplib.SMTP", create=True) as smtplib_mock:
            outcome = module.plugin(srv, item)

            # Specifically examine the email body.
            body = smtplib_mock.mock_calls[5].args[2]
            assert body.startswith('Content-Type: text/plain; charset="utf-8"')
            assert "Content-Transfer-Encoding: base64" in body
            assert "4pq9IE5vdGlmaWNhdGlvbiBtZXNzYWdlIOKavQ==" in body

        assert outcome is True


@pytest.mark.skipif(sys.version_info < (3, 8), reason="This test only works on Python >= 3.8")
def test_smtp_html(srv, caplog):
    """
    Pretend sending an HTML message with SMTP and verify API calls
    and message encoding matches the expectations.
    """

    module = load_module_from_file("mqttwarn/services/smtp.py")

    item = Item(
        config={
            "server": "localhost:25",
            "sender": "mqttwarn <mqttwarn@localhost>",
            "username": "foobar",
            "password": "bazqux",
            "starttls": True,
            "htmlmsg": True,
        },
        target="test",
        addrs=["foo@example.org", "bar@example.org"],
        message="⚽ Notification message ⚽",
    )

    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):
        with mock.patch("smtplib.SMTP", create=True) as smtplib_mock:
            outcome = module.plugin(srv, item)

            # Specifically examine the email body.
            body = smtplib_mock.mock_calls[5].args[2]
            assert body.startswith("Content-Type: multipart/alternative")
            assert 'Content-Type: text/plain; charset="utf-8"' in body
            assert "Content-Transfer-Encoding: base64" in body
            assert "4pq9IE5vdGlmaWNhdGlvbiBtZXNzYWdlIOKavQ==" in body

        assert outcome is True


def test_smtp_no_addresses(srv, caplog):
    """
    When sending a message without addressees, mail sending will be skipped
    with a corresponding log message.
    """

    module = load_module_from_file("mqttwarn/services/smtp.py")

    item = Item(
        config={
            "server": "localhost:25",
            "sender": "mqttwarn <mqttwarn@localhost>",
            "username": "foobar",
            "password": "bazqux",
            "starttls": True,
            "htmlmsg": True,
        },
        target="test",
        addrs=[],
        message="⚽ Notification message ⚽",
    )

    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):
        outcome = module.plugin(srv, item)
        assert outcome is False

    assert "Skipped sending SMTP notification to test, no addresses configured" in caplog.messages


def test_smtp_submit_error(srv, caplog):
    """
    Verify the outcome of the service plugin when SMTP submission fails.
    """

    module = load_module_from_file("mqttwarn/services/smtp.py")

    item = Item(
        config={
            "server": "localhost:25",
            "sender": "mqttwarn <mqttwarn@localhost>",
            "username": "foobar",
            "password": "bazqux",
            "starttls": True,
            "htmlmsg": True,
        },
        target="test",
        addrs=["foo@example.org", "bar@example.org"],
        message="⚽ Notification message ⚽",
    )

    item = Struct(**item.asdict())

    with caplog.at_level(logging.DEBUG):
        with mock.patch("smtplib.SMTP", create=True) as smtplib_mock:

            smtplib_mock.side_effect = TimeoutError("Something failed")
            outcome = module.plugin(srv, item)

        assert outcome is False

    assert (
        "Error sending notification to SMTP recipient test, addresses: "
        "['foo@example.org', 'bar@example.org']. Exception: Something failed" in caplog.messages
    )
