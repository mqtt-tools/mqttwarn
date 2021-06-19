# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock
from unittest.mock import call, PropertyMock

from surrogate import surrogate

from mqttwarn.util import load_module_by_name, load_module_from_file
from mqttwarn.model import ProcessorItem as Item


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


@surrogate("puka")
@mock.patch("puka.Client", create=True)
def test_amqp_success(mock_puka_client, srv, caplog):
    module = load_module_by_name("mqttwarn.services.amqp")

    exchange, routing_key = ["name_of_exchange", "my_routing_key"]
    item = Item(
        config={"uri": "amqp://user:password@localhost:5672/"},
        target="test",
        addrs=[exchange, routing_key],
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        outcome = module.plugin(srv, item)

        assert mock_puka_client.mock_calls == [
            mock.call("amqp://user:password@localhost:5672/"),
            call().connect(),
            call().wait(mock.ANY),
            call().basic_publish(
                exchange="name_of_exchange",
                routing_key="my_routing_key",
                headers={
                    "content_type": "text/plain",
                    "x-agent": "mqttwarn",
                    "delivery_mode": 1,
                },
                body="⚽ Notification message ⚽",
            ),
            call().wait(mock.ANY),
            call().close(),
        ]

        assert outcome is True
        assert "AMQP publish to test [name_of_exchange/my_routing_key]" in caplog.text
        assert "Successfully published AMQP notification" in caplog.text


@surrogate("puka")
def test_amqp_failure(srv, caplog):
    module = load_module_by_name("mqttwarn.services.amqp")

    exchange, routing_key = ["name_of_exchange", "my_routing_key"]
    item = Item(
        config={"uri": "amqp://user:password@localhost:5672/"},
        target="test",
        addrs=[exchange, routing_key],
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        mock_connection = mock.MagicMock()

        # Make the call to `basic_publish` raise an exception.
        def error(*args, **kwargs):
            raise Exception("something failed")

        mock_connection.basic_publish = error

        with mock.patch(
            "puka.Client", side_effect=[mock_connection], create=True
        ) as mock_client:

            outcome = module.plugin(srv, item)

            assert mock_client.mock_calls == [
                mock.call("amqp://user:password@localhost:5672/"),
            ]
            assert mock_connection.mock_calls == [
                call.connect(),
                call.wait(mock.ANY),
            ]

            assert outcome is False
            assert (
                "AMQP publish to test [name_of_exchange/my_routing_key]" in caplog.text
            )
            assert (
                "Error on AMQP publish to test [name_of_exchange/my_routing_key]: something failed"
                in caplog.text
            )


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


@surrogate("apprise")
@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_success(apprise_asset, apprise_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apprise.py")

        item = Item(
            config={
                "baseuri": "mailtos://smtp_username:smtp_password@mail.example.org"
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
                "mailtos://smtp_username:smtp_password@mail.example.org?from=None&to=foo@example.org,bar@example.org"
            ),
            call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
            call().notify().__bool__(),
        ]

        assert outcome is True
        assert (
            "Sending notification to Apprise test, addresses: ['foo@example.org', 'bar@example.org']"
            in caplog.text
        )
        assert "Successfully sent message using Apprise" in caplog.text


@surrogate("apprise")
@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_failure_no_addresses(apprise_asset, apprise_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apprise.py")

        item = Item(
            config={
                "baseuri": "mailtos://smtp_username:smtp_password@mail.example.org"
            },
            target="test",
            addrs=[],
            title="⚽ Message title ⚽",
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert apprise_mock.mock_calls == []

        assert outcome is False
        assert (
            "Skipped sending notification to Apprise test, no addresses configured"
            in caplog.text
        )


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
                module = load_module_from_file("mqttwarn/services/apprise.py")

                item = Item(
                    config={
                        "baseuri": "mailtos://smtp_username:smtp_password@mail.example.org"
                    },
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
                        "mailtos://smtp_username:smtp_password@mail.example.org?from=None&to=foo@example.org,bar@example.org"
                    ),
                ]

                assert outcome is False
                assert (
                    "Sending notification to Apprise test, addresses: ['foo@example.org', 'bar@example.org']"
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
                module = load_module_from_file("mqttwarn/services/apprise.py")

                item = Item(
                    config={
                        "baseuri": "mailtos://smtp_username:smtp_password@mail.example.org"
                    },
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
                        "mailtos://smtp_username:smtp_password@mail.example.org?from=None&to=foo@example.org,bar@example.org"
                    ),
                ]

                assert outcome is False
                assert (
                    "Sending notification to Apprise test, addresses: ['foo@example.org', 'bar@example.org']"
                    in caplog.text
                )
                assert "Error sending message to test: something failed" in caplog.text


@surrogate("apprise")
@mock.patch("apprise.Apprise", create=True)
@mock.patch("apprise.AppriseAsset", create=True)
def test_apprise_success_with_sender(apprise_asset, apprise_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/apprise.py")

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
                "mailtos://smtp_username:smtp_password@mail.example.org?from=example@example.org&to=foo@example.org,bar@example.org&name=Max Mustermann"
            ),
            call().notify(body="⚽ Notification message ⚽", title="⚽ Message title ⚽"),
            call().notify().__bool__(),
        ]

        assert outcome is True
        assert "Successfully sent message using Apprise" in caplog.text


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
def test_asterisk_success(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {"login.return_value": 42, "originate.return_value": 42}
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().originate(
                "SIP/avaya/0123456789",
                2222,
                context="default",
                priority="1",
                caller_id=2222,
                variables={"text": "⚽ Notification message ⚽"},
            ),
            call().logoff(),
            call().close(),
        ]

        assert outcome is True
        assert "Authentication 42" in caplog.text
        assert "Call 42" in caplog.text


class ManagerSocketException(Exception):
    pass


class ManagerAuthException(Exception):
    pass


class ManagerException(Exception):
    pass


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch(
    "asterisk.manager.ManagerSocketException", ManagerSocketException, create=True
)
def test_asterisk_failure_no_connection(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {"connect.side_effect": ManagerSocketException("something failed")}
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().close(),
        ]

        assert outcome is False
        assert "Error connecting to the manager: something failed" in caplog.text


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch(
    "asterisk.manager.ManagerSocketException", ManagerSocketException, create=True
)
@mock.patch("asterisk.manager.ManagerAuthException", ManagerAuthException, create=True)
def test_asterisk_failure_login_invalid(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {"login.side_effect": ManagerAuthException("something failed")}
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().close(),
        ]

        assert outcome is False
        assert "Error logging in to the manager: something failed" in caplog.text


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch(
    "asterisk.manager.ManagerSocketException", ManagerSocketException, create=True
)
@mock.patch("asterisk.manager.ManagerAuthException", ManagerAuthException, create=True)
@mock.patch("asterisk.manager.ManagerException", ManagerException, create=True)
def test_asterisk_failure_originate_croaks(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {
            "login.return_value": 42,
            "originate.side_effect": ManagerException("something failed"),
        }
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().originate(
                "SIP/avaya/0123456789",
                2222,
                context="default",
                priority="1",
                caller_id=2222,
                variables={"text": "⚽ Notification message ⚽"},
            ),
            call().close(),
        ]

        assert outcome is False
        assert "Error: something failed" in caplog.text


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch(
    "asterisk.manager.ManagerSocketException", ManagerSocketException, create=True
)
@mock.patch("asterisk.manager.ManagerAuthException", ManagerAuthException, create=True)
@mock.patch("asterisk.manager.ManagerException", ManagerException, create=True)
def test_asterisk_success_with_broken_close(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {
            "login.return_value": 42,
            "originate.return_value": 42,
            "close.side_effect": ManagerSocketException("something failed"),
        }
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().originate(
                "SIP/avaya/0123456789",
                2222,
                context="default",
                priority="1",
                caller_id=2222,
                variables={"text": "⚽ Notification message ⚽"},
            ),
            call().logoff(),
            call().close(),
        ]

        assert outcome is True


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

        with mock.patch(
            "requests.get", side_effect=Exception("something failed")
        ) as requests_mock:
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
        assert (
            "Failed to send message to autoremote service: something failed"
            in caplog.text
        )


def test_azure_iot_success_string(srv, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/azure_iot.py")

        mqtt_publish_mock = mock.MagicMock()
        module.mqtt = mqtt_publish_mock

        outcome = module.plugin(srv, item)
        mqtt_publish_mock.single.assert_called_once_with(
            "devices/device-id/messages/events/",
            bytearray(b"\xe2\x9a\xbd Notification message \xe2\x9a\xbd"),
            auth={
                "username": "acmehub.azure-devices.net/device-id/?api-version=2018-06-30",
                "password": "SharedAccessSignature sr=...",
            },
            tls={
                "ca_certs": None,
                "certfile": None,
                "keyfile": None,
                "tls_version": mock.ANY,
                "ciphers": None,
                "cert_reqs": mock.ANY,
            },
            hostname="acmehub.azure-devices.net",
            port=8883,
            protocol=4,
            qos=0,
            retain=False,
            client_id="device-id",
        )

        assert outcome is True
        assert (
            "Publishing to Azure IoT Hub for target=test (device-id): devices/device-id/messages/events/ 'bytearray(b'\\xe2\\x9a\\xbd Notification message \\xe2\\x9a\\xbd')'"
            in caplog.text
        )


def test_azure_iot_success_bytes(srv, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message=b"### Notification message ###",
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/azure_iot.py")

        mqtt_publish_mock = mock.MagicMock()
        module.mqtt = mqtt_publish_mock

        outcome = module.plugin(srv, item)
        mqtt_publish_mock.single.assert_called_once_with(
            "devices/device-id/messages/events/",
            bytearray(b"### Notification message ###"),
            auth={
                "username": "acmehub.azure-devices.net/device-id/?api-version=2018-06-30",
                "password": "SharedAccessSignature sr=...",
            },
            tls={
                "ca_certs": None,
                "certfile": None,
                "keyfile": None,
                "tls_version": mock.ANY,
                "ciphers": None,
                "cert_reqs": mock.ANY,
            },
            hostname="acmehub.azure-devices.net",
            port=8883,
            protocol=4,
            qos=0,
            retain=False,
            client_id="device-id",
        )

        assert outcome is True
        assert (
            "Publishing to Azure IoT Hub for target=test (device-id): devices/device-id/messages/events/ 'b'### Notification message ###''"
            in caplog.text
        )


def test_azure_iot_failure_wrong_qos(srv, caplog):

    item = Item(
        config={"iothubname": "acmehub", "qos": 999},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/azure_iot.py")

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "Only QoS 0 or 1 allowed for Azure IoT Hub, not '999'" in caplog.text


def test_azure_iot_failure_invalid_message(srv, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
    )

    with mock.patch.object(Item, "message", new_callable=PropertyMock) as msg_mock:
        msg_mock.side_effect = Exception("something failed")

        with caplog.at_level(logging.DEBUG):

            module = load_module_from_file("mqttwarn/services/azure_iot.py")

            outcome = module.plugin(srv, item)

            assert outcome is False
            assert (
                "Unable to prepare message for target=test: something failed"
                in caplog.text
            )


def test_azure_iot_failure_mqtt_publish(srv, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message="⚽ Notification message ⚽",
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/azure_iot.py")

        mqtt_publish_mock = mock.MagicMock(side_effect=Exception("something failed"))
        module.mqtt.single = mqtt_publish_mock

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert (
            "Unable to publish to Azure IoT Hub for target=test (device-id): something failed"
            in caplog.text
        )


def test_carbon_success_metric_value_timestamp(srv, caplog):

    item = Item(
        target="test", addrs=["localhost", 2003], message="foo 42.42 1623887596", data={}
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(),
            call().connect(("localhost", 2003)),
            call().sendall("foo 42.42 1623887596\n"),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to carbon: foo 42.42 1623887596" in caplog.text


def test_carbon_success_metric_value(srv, caplog):

    item = Item(
        target="test", addrs=["localhost", 2003], message="foo 42.42", data={}
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(),
            call().connect(("localhost", 2003)),
            call().sendall(mock.ANY),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to carbon: foo 42.42" in caplog.text


def test_carbon_success_value(srv, caplog):

    item = Item(
        target="test", addrs=["localhost", 2003], message="42.42", data={}
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(),
            call().connect(("localhost", 2003)),
            call().sendall(mock.ANY),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to carbon: ohno 42.42" in caplog.text


def test_carbon_success_value_metric_from_topic(srv, caplog):

    item = Item(
        target="test", addrs=["localhost", 2003], message="42.42", data={"topic": "foo/bar"}
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(),
            call().connect(("localhost", 2003)),
            call().sendall(mock.ANY),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to carbon: foo.bar 42.42" in caplog.text


def test_carbon_success_value_metric_from_topic_with_leading_slash(srv, caplog):

    item = Item(
        target="test", addrs=["localhost", 2003], message="42.42", data={"topic": "/foo/bar"}
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(),
            call().connect(("localhost", 2003)),
            call().sendall(mock.ANY),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to carbon: foo.bar 42.42" in caplog.text


def test_carbon_failure_invalid_configuration(srv, caplog):

    item = Item(target="test", addrs=["172.16.153.110", "foobar"])

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "Configuration for target `carbon' is incorrect" in caplog.text


def test_carbon_failure_empty_message(srv, caplog):

    item = Item(target="test", addrs=["172.16.153.110", 2003])

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "target `carbon': cannot split string" in caplog.text


def test_carbon_failure_invalid_message_format(srv, caplog):

    item = Item(
        target="test",
        addrs=["172.16.153.110", 2003],
        message="foo bar baz qux",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        outcome = module.plugin(srv, item)

        assert outcome is False
        assert "target `carbon': error decoding message" in caplog.text


def test_carbon_failure_connect(srv, caplog):

    item = Item(
        target="test", addrs=["localhost", 2003], message="foo 42.42 1623887596", data={}
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/carbon.py")

        attrs = {"connect.side_effect": Exception("something failed")}
        socket_mock = mock.MagicMock()
        socket_mock.return_value = mock.MagicMock(**attrs)
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [call(), call().connect(("localhost", 2003))]

        assert outcome is False
        assert "Sending to carbon: foo 42.42 1623887596" in caplog.text
        assert (
            "Cannot send to carbon service localhost:2003: something failed"
            in caplog.text
        )
