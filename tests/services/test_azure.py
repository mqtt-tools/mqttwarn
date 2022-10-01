# -*- coding: utf-8 -*-
# (c) 2021-2022 The mqttwarn developers
from unittest import mock
from unittest.mock import PropertyMock

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


def test_azure_iot_success_string(srv, mocker, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message="⚽ Notification message ⚽",
    )

    module = load_module_from_file("mqttwarn/services/azure_iot.py")

    mqtt_single = mocker.patch.object(module.mqtt, "single")

    outcome = module.plugin(srv, item)
    mqtt_single.assert_called_once_with(
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
        "Publishing to Azure IoT Hub for target=test (device-id): devices/device-id/messages/events/ "
        "'bytearray(b'\\xe2\\x9a\\xbd Notification message \\xe2\\x9a\\xbd')'" in caplog.messages
    )


def test_azure_iot_success_bytes(srv, mocker, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message=b"### Notification message ###",
    )

    module = load_module_from_file("mqttwarn/services/azure_iot.py")

    mqtt_single = mocker.patch.object(module.mqtt, "single")

    outcome = module.plugin(srv, item)
    mqtt_single.assert_called_once_with(
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
        "Publishing to Azure IoT Hub for target=test (device-id): devices/device-id/messages/events/ "
        "'b'### Notification message ###''" in caplog.messages
    )


def test_azure_iot_failure_wrong_qos(srv, caplog):

    item = Item(
        config={"iothubname": "acmehub", "qos": 999},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message="⚽ Notification message ⚽",
    )

    module = load_module_from_file("mqttwarn/services/azure_iot.py")

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Only QoS 0 or 1 allowed for Azure IoT Hub, not '999'" in caplog.messages


def test_azure_iot_failure_invalid_message(srv, mocker, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
    )

    mocker.patch.object(Item, "message", new_callable=PropertyMock, side_effect=Exception("something failed"))

    module = load_module_from_file("mqttwarn/services/azure_iot.py")

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Unable to prepare message for target=test: something failed" in caplog.messages


def test_azure_iot_failure_mqtt_publish(srv, mocker, caplog):

    item = Item(
        config={"iothubname": "acmehub"},
        target="test",
        addrs=["device-id", "SharedAccessSignature sr=..."],
        message="⚽ Notification message ⚽",
    )

    module = load_module_from_file("mqttwarn/services/azure_iot.py")

    mocker.patch.object(module.mqtt, "single", side_effect=Exception("something failed"))

    outcome = module.plugin(srv, item)

    assert outcome is False
    assert "Unable to publish to Azure IoT Hub for target=test (device-id): something failed" in caplog.messages
