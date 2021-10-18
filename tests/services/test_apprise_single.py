# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock
from unittest.mock import call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file
from surrogate import surrogate


@surrogate("apprise")
@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_success(apprise_asset, apprise_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apprise_single.py")

        item = Item(
            config={"baseuri": "mailtos://smtp_username:smtp_password@mail.example.org"},
            target="test",
            addrs=["foo@example.org", "bar@example.org"],
            title="⚽ Message title ⚽",
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert apprise_mock.mock_calls == [
            call(asset=mock.ANY),
            call().add(
                "mailtos://smtp_username:smtp_password@mail.example.org?to=foo%40example.org%2Cbar%40example.org"
            ),
            call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
            call().notify().__bool__(),
        ]

        assert outcome is True
        assert (
            "Sending notification to Apprise. target=test, addresses=['foo@example.org', 'bar@example.org']"
            in caplog.text
        )
        assert "Successfully sent message using Apprise" in caplog.text


@surrogate("apprise")
@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_success_no_addresses(apprise_asset, apprise_mock, srv, caplog):
    """
    Some Apprise notifiers don't need any target address information.
    Proof that also works by processing an `Item` with no `target`
    and `addrs` attributes supplied.
    """

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apprise_single.py")

        item = Item(
            config={"baseuri": "json://localhost:1234/mqtthook"},
            title="⚽ Message title ⚽",
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert apprise_mock.mock_calls == [
            call(asset=mock.ANY),
            call().add("json://localhost:1234/mqtthook"),
            call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
            call().notify().__bool__(),
        ]

        assert outcome is True
        assert "Sending notification to Apprise. target=None, addresses=[]" in caplog.messages
        assert "Successfully sent message using Apprise" in caplog.messages


@surrogate("apprise")
def test_apprise_failure_notify(srv, caplog):

    with caplog.at_level(logging.DEBUG):

        mock_connection = mock.MagicMock()

        # Make the call to `notify` signal failure.
        def error(*args, **kwargs):
            return False

        mock_connection.notify = error

        with mock.patch(
            "apprise.Apprise", side_effect=[mock_connection], create=True
        ) as mock_client:
            with mock.patch("apprise.AppriseAsset", create=True) as mock_asset:
                module = load_module_from_file("mqttwarn/services/apprise_single.py")

                item = Item(
                    config={"baseuri": "mailtos://smtp_username:smtp_password@mail.example.org"},
                    target="test",
                    addrs=["foo@example.org", "bar@example.org"],
                    title="⚽ Message title ⚽",
                    message="⚽ Notification message ⚽",
                )

                outcome = module.plugin(srv, item)

                assert mock_client.mock_calls == [
                    mock.call(asset=mock.ANY),
                ]
                assert mock_connection.mock_calls == [
                    call.add(
                        "mailtos://smtp_username:smtp_password@mail.example.org?to=foo%40example.org%2Cbar%40example.org"
                    ),
                ]

                assert outcome is False
                assert (
                    "Sending notification to Apprise. target=test, addresses=['foo@example.org', 'bar@example.org']"
                    in caplog.text
                )
                assert "Sending message using Apprise failed" in caplog.text


@surrogate("apprise")
def test_apprise_error(srv, caplog):

    with caplog.at_level(logging.DEBUG):

        mock_connection = mock.MagicMock()

        # Make the call to `notify` raise an exception.
        def error(*args, **kwargs):
            raise Exception("something failed")

        mock_connection.notify = error

        with mock.patch(
            "apprise.Apprise", side_effect=[mock_connection], create=True
        ) as mock_client:
            with mock.patch("apprise.AppriseAsset", create=True) as mock_asset:
                module = load_module_from_file("mqttwarn/services/apprise_single.py")

                item = Item(
                    config={"baseuri": "mailtos://smtp_username:smtp_password@mail.example.org"},
                    target="test",
                    addrs=["foo@example.org", "bar@example.org"],
                    title="⚽ Message title ⚽",
                    message="⚽ Notification message ⚽",
                )

                outcome = module.plugin(srv, item)

                assert mock_client.mock_calls == [
                    mock.call(asset=mock.ANY),
                ]
                assert mock_connection.mock_calls == [
                    call.add(
                        "mailtos://smtp_username:smtp_password@mail.example.org?to=foo%40example.org%2Cbar%40example.org"
                    ),
                ]

                assert outcome is False
                assert (
                    "Sending notification to Apprise. target=test, addresses=['foo@example.org', 'bar@example.org']"
                    in caplog.messages
                )
                assert (
                    "Sending message using Apprise failed. target=test, error=something failed"
                    in caplog.messages
                )


@surrogate("apprise")
@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_success_with_sender(apprise_asset, apprise_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apprise_single.py")

        item = Item(
            config={
                "baseuri": "mailtos://smtp_username:smtp_password@mail.example.org",
                "sender": "example@example.org",
                "sender_name": "Max Mustermann",
            },
            target="test",
            addrs=["foo@example.org", "bar@example.org"],
            title="⚽ Message title ⚽",
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert apprise_mock.mock_calls == [
            call(asset=mock.ANY),
            call().add(
                "mailtos://smtp_username:smtp_password@mail.example.org?from=example%40example.org&to=foo%40example.org%2Cbar%40example.org&name=Max+Mustermann"
            ),
            call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
            call().notify().__bool__(),
        ]

        assert outcome is True
        assert "Successfully sent message using Apprise" in caplog.text
