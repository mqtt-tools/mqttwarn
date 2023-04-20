# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
from unittest import mock
from unittest.mock import call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_by_name


@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_multi_basic_success(apprise_asset, apprise_mock, srv, caplog):

    module = load_module_by_name("mqttwarn.services.apprise_multi")

    item = Item(
        addrs=[
            {"baseuri": "json://localhost:1234/mqtthook"},
            {"baseuri": "json://daq.example.org:5555/foobar"},
        ],
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
    )

    outcome = module.plugin(srv, item)

    assert apprise_mock.mock_calls == [
        call(asset=mock.ANY),
        call().add("json://localhost:1234/mqtthook"),
        call().add("json://daq.example.org:5555/foobar"),
        call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
        call().notify().__bool__(),
    ]

    assert outcome is True
    assert (
        "Sending notification to Apprise. target=None, addresses=["
        "{'baseuri': 'json://localhost:1234/mqtthook'}, "
        "{'baseuri': 'json://daq.example.org:5555/foobar'}"
        "]" in caplog.messages
    )
    assert "Successfully sent message using Apprise" in caplog.messages


@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_multi_mailto_success(apprise_asset, apprise_mock, srv, caplog):

    module = load_module_by_name("mqttwarn.services.apprise_multi")

    item = Item(
        addrs=[
            {
                "baseuri": "mailtos://smtp_username:smtp_password@mail.example.org",
                "recipients": ["foo@example.org", "bar@example.org"],
                "sender": "monitoring@example.org",
                "sender_name": "Example Monitoring",
            }
        ],
        title="⚽ Message title ⚽",
        message="⚽ Notification message ⚽",
    )

    outcome = module.plugin(srv, item)

    assert apprise_mock.mock_calls == [
        call(asset=mock.ANY),
        call().add(
            "mailtos://smtp_username:smtp_password@mail.example.org"
            "?to=foo%40example.org%2Cbar%40example.org&from=monitoring%40example.org&name=Example+Monitoring"
        ),
        call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
        call().notify().__bool__(),
    ]

    assert outcome is True
    assert (
        "Sending notification to Apprise. target=None, addresses=["
        "{"
        "'baseuri': 'mailtos://smtp_username:smtp_password@mail.example.org', "
        "'recipients': ['foo@example.org', 'bar@example.org'], "
        "'sender': 'monitoring@example.org', 'sender_name': 'Example Monitoring'}]" in caplog.messages
    )
    assert "Successfully sent message using Apprise" in caplog.messages


def test_apprise_multi_failure_notify(srv, caplog):

    mock_connection = mock.MagicMock()

    # Make the call to `notify` signal failure.
    def error(*args, **kwargs):
        return False

    mock_connection.notify = error

    with mock.patch("apprise.Apprise", side_effect=[mock_connection], create=True) as mock_client:
        with mock.patch("apprise.AppriseAsset", create=True):
            module = load_module_by_name("mqttwarn.services.apprise_multi")

            item = Item(
                addrs=[{"baseuri": "json://localhost:1234/mqtthook"}],
                title="⚽ Message title ⚽",
                message="⚽ Notification message ⚽",
            )

            outcome = module.plugin(srv, item)

            assert mock_client.mock_calls == [
                mock.call(asset=mock.ANY),
            ]
            assert mock_connection.mock_calls == [
                call.add("json://localhost:1234/mqtthook"),
            ]

            assert outcome is False
            assert (
                "Sending notification to Apprise. target=None, "
                "addresses=[{'baseuri': 'json://localhost:1234/mqtthook'}]" in caplog.messages
            )
            assert "Sending message using Apprise failed" in caplog.messages


def test_apprise_multi_error(srv, caplog):

    mock_connection = mock.MagicMock()

    # Make the call to `notify` raise an exception.
    def error(*args, **kwargs):
        raise Exception("something failed")

    mock_connection.notify = error

    with mock.patch("apprise.Apprise", side_effect=[mock_connection], create=True) as mock_client:
        with mock.patch("apprise.AppriseAsset", create=True):
            module = load_module_by_name("mqttwarn.services.apprise_multi")

            item = Item(
                addrs=[{"baseuri": "json://localhost:1234/mqtthook"}],
                title="⚽ Message title ⚽",
                message="⚽ Notification message ⚽",
            )

            outcome = module.plugin(srv, item)

            assert mock_client.mock_calls == [
                mock.call(asset=mock.ANY),
            ]
            assert mock_connection.mock_calls == [
                call.add("json://localhost:1234/mqtthook"),
            ]

            assert outcome is False
            assert (
                "Sending notification to Apprise. target=None, "
                "addresses=[{'baseuri': 'json://localhost:1234/mqtthook'}]" in caplog.messages
            )
            assert "Sending message using Apprise failed. target=None, error=something failed" in caplog.messages
