# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock
from unittest.mock import PropertyMock

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


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
            assert "Unable to prepare message for target=test: something failed" in caplog.text


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
