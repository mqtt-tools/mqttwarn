# -*- coding: utf-8 -*-
# (c) 2022 The mqttwarn developers
"""
Full system tests verifying mqttwarn end-to-end, using an MQTT broker.
"""
import json
import os
import sys

import pytest
from pytest_mqtt import MqttMessage

from mqttwarn.configuration import load_configuration
from mqttwarn.core import bootstrap, connect
from mqttwarn.model import StatusInformation
from tests import configfile_no_functions
from tests.util import delay, mqtt_process

if os.getenv("GITHUB_ACTIONS") == "true" and sys.platform != "linux":
    raise pytest.skip(msg="On GHA, Mosquitto via Docker is only available on Linux", allow_module_level=True)


# Mark all test case functions within this module with `e2e`.
pytestmark = pytest.mark.e2e

# Configure `capmqtt` to return `MqttMessage.payload` as `str`, decoded from `utf-8`.
capmqtt_decode_utf8 = True


def test_system_status_publish(mosquitto, tmp_ini, caplog, capmqtt):
    """
    A full system test verifying the `status_publish` feature.
    It approves "Does mqttwarn boot and emit system messages to `mqttwarn/$SYS` correctly?".
    """

    tmp_ini.write_text(
        """
[defaults]
; Publish mqttwarn status information (retained)
status_publish = True
status_topic = mqttwarn-testdrive/$SYS
    """
    )

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=tmp_ini)
    bootstrap(config=config)

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc)

    # Let mqttwarn emit messages to `mqttwarn/$SYS`.
    delay()

    # Verify log output.
    assert "No services defined" in caplog.messages
    assert "Attempting connection to MQTT broker localhost:1883" in caplog.messages
    assert "Setting LWT to clients/mqttwarn" in caplog.messages
    assert "Publishing status information to mqttwarn-testdrive/$SYS" in caplog.messages
    assert "Starting 1 worker threads" in caplog.messages
    assert "Job queue has 0 items to process" in caplog.messages
    assert "Connected to MQTT broker, subscribing to topics" in caplog.messages

    # Verify MQTT messages.
    si = StatusInformation()
    assert (
        MqttMessage(topic="mqttwarn-testdrive/$SYS/version", payload=si.mqttwarn_version, userdata=None)
        in capmqtt.messages
    )
    assert (
        MqttMessage(topic="mqttwarn-testdrive/$SYS/platform", payload=si.os_platform, userdata=None) in capmqtt.messages
    )
    assert (
        MqttMessage(topic="mqttwarn-testdrive/$SYS/python/version", payload=si.python_version, userdata=None)
        in capmqtt.messages
    )
    # assert MqttMessage(topic="clients/mqttwarn", payload="1", userdata=None) in capmqtt.messages

    mqttc.disconnect()


def test_system_dispatch_to_log_service_plaintext(mosquitto, caplog, capmqtt):
    """
    A full system test verifying the notification message dispatching feature with a plaintext message.
    It approves "Does mqttwarn boot and process messages correctly?".
    Within this test case, it uses the `log` service plugin.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=configfile_no_functions)
    bootstrap(config=config)

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc, loops=3)

    # Submit a message to the broker.
    capmqtt.publish(topic="test/log-1", payload="foobar")

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=4)

    # Verify log output.
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Subscribing to test/log-1 (qos=0)" in caplog.messages

    assert "Message received on test/log-1: foobar" in caplog.messages
    assert "Section [test/log-1] matches message on test/log-1, processing it" in caplog.messages
    assert "Decoding JSON failed: Expecting value: line 1 column 1 (char 0). payload=foobar" in caplog.messages
    assert "Message on test/log-1 going to log:info" in caplog.messages
    assert "New `log:info' job: test/log-1" in caplog.messages
    assert "Processor #0 is handling: `log' for info" in caplog.messages
    assert "Formatting message with function failed: {name}: {value}" in caplog.messages
    assert "Invoking service plugin for `log'" in caplog.messages
    assert ("mqttwarn.services.log", 20, "foobar") in caplog.record_tuples
    assert "Job queue has 0 items to process" in caplog.messages

    # Verify MQTT messages.
    assert MqttMessage(topic="test/log-1", payload="foobar", userdata=None) in capmqtt.messages

    mqttc.disconnect()


def test_system_dispatch_to_log_service_json(mosquitto, caplog, capmqtt):
    """
    A full system test verifying the notification message dispatching feature with a JSON message.
    It approves "Does mqttwarn boot and process messages correctly?".
    Within this test case, it uses the `log` service plugin.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=configfile_no_functions)
    bootstrap(config=config)

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc)

    # Submit a message to the broker.
    capmqtt.publish(topic="test/log-1", payload=json.dumps({"name": "foo", "value": "bar"}))

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=4)

    # Verify log output.
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Subscribing to test/log-1 (qos=0)" in caplog.messages

    assert 'Message received on test/log-1: {"name": "foo", "value": "bar"}' in caplog.messages
    assert "Section [test/log-1] matches message on test/log-1, processing it" in caplog.messages
    assert "Message on test/log-1 going to log:info" in caplog.messages
    assert "New `log:info' job: test/log-1" in caplog.messages
    assert "Processor #0 is handling: `log' for info" in caplog.messages
    assert "Invoking service plugin for `log'" in caplog.messages
    assert ("mqttwarn.services.log", 20, "foo: bar") in caplog.record_tuples
    assert "Job queue has 0 items to process" in caplog.messages

    # Verify MQTT messages.
    assert MqttMessage(topic="test/log-1", payload='{"name": "foo", "value": "bar"}', userdata=None) in capmqtt.messages

    mqttc.disconnect()


def test_system_dispatch_to_file_service_binary(mosquitto, caplog, capmqtt, pytestconfig):
    """
    A full system test verifying the notification message dispatching feature with a binary message.
    It approves "Does mqttwarn boot and process messages correctly?".
    Within this test case, it uses the `file` service plugin.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=configfile_no_functions)
    bootstrap(config=config)

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc)

    # Submit a message to the broker.
    capmqtt.publish(topic="test/file-1", payload=b"foobar")

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=4)

    # Verify log output.
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Subscribing to test/file-1 (qos=0)" in caplog.messages

    assert "Message received on test/file-1: foobar" in caplog.messages
    assert "Section [test/file-1] matches message on test/file-1, processing it" in caplog.messages
    assert "Decoding JSON failed: Expecting value: line 1 column 1 (char 0). payload=foobar" in caplog.messages
    assert "Message on test/file-1 going to file:spool-binary" in caplog.messages
    assert "New `file:spool-binary' job: test/file-1" in caplog.messages
    assert "Processor #0 is handling: `file' for spool-binary" in caplog.messages
    assert "Invoking service plugin for `file'" in caplog.messages
    assert ("mqttwarn.services.file", 20, "Writing to file `/tmp/mqttwarn-test-spool.jpg'") in caplog.record_tuples
    assert "Job queue has 0 items to process" in caplog.messages

    # Verify MQTT messages.
    # Remark: Message payload must still be compared as string, because `pytest-mqtt` decodes it,
    #         as it has been configured with `capmqtt_decode_utf8`.
    assert MqttMessage(topic="test/file-1", payload="foobar", userdata=None) in capmqtt.messages

    mqttc.disconnect()
