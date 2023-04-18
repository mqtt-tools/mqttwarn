# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
"""
Test accompanying "Forwarding Frigate events to Ntfy".
Full system test verifying mqttwarn end-to-end, using an MQTT broker.
"""
import os
import sys
from pathlib import Path

import pytest

from mqttwarn.configuration import load_configuration
from mqttwarn.core import bootstrap, connect
from tests.util import mqtt_process

if os.getenv("GITHUB_ACTIONS") == "true" and sys.platform != "linux":
    raise pytest.skip(msg="On GHA, Mosquitto via Docker is only available on Linux", allow_module_level=True)


# Mark all test case functions within this module with `e2e`.
pytestmark = pytest.mark.e2e

# Configure `capmqtt` to not decode `MqttMessage.payload` from `utf-8`, to make it possible to process binary data.
capmqtt_decode_utf8 = False

HERE = Path(__file__).parent
ASSETS = HERE.joinpath("assets")


def test_frigate_event_new(mosquitto, ntfy_service, caplog, capmqtt):
    """
    A full system test verifying the "Forwarding Frigate events to Ntfy" example.
    This test case submits the `frigate-event-new-good.json` file as MQTT event message.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=HERE / "frigate.ini")
    bootstrap(config=config)

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc)

    # Publish the JSON event message.
    # cat frigate-event-new-good.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    payload_event = open(ASSETS / "frigate-event-new-good.json").read()
    capmqtt.publish(topic="frigate/events", payload=payload_event)

    # Publish the snapshot image.
    # mosquitto_pub -f goat.jpg -t 'frigate/cam-testdrive/goat/snapshot'
    #payload_image = open(HERE / "goat.jpg", "rb").read()
    #capmqtt.publish(topic="frigate/cam-testdrive/goat/snapshot", payload=payload_image)
    capmqtt.publish(topic="frigate/cam-testdrive/goat/snapshot", payload=b"foobar")

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=6)

    # Verify log output.
    assert 'Successfully loaded service "apprise-ntfy"' in caplog.messages
    assert 'Successfully loaded service "store-jpeg"' in caplog.messages

    assert "Subscribing to frigate/events (qos=0)" in caplog.messages
    assert "Subscribing to frigate/+/+/snapshot (qos=0)" in caplog.messages

    assert "MQTT message received: MqttMessage(topic='frigate/events'" in caplog.text
    assert "Section [frigate/events] matches message on frigate/events, processing it" in caplog.messages
    assert "Message on frigate/events going to apprise-ntfy" in caplog.messages
    assert "Invoking service plugin for `apprise-ntfy'" in caplog.messages
    assert "ntfy Payload: {'topic': 'frigate', 'title': 'goat entered lawn at 2023-04-06 14:31:46.638857+00:00', 'message': 'goat was in barn'}" in caplog.messages
    assert "ntfy Headers: {'User-Agent': 'Apprise', 'Content-Type': 'application/json', 'X-Icon': 'https://github.com/caronc/apprise/raw/master/apprise/assets/themes/default/apprise-info-256x256.png', 'X-Click': 'https://frigate/events?camera=cam-testdrive&label=goat&zone=lawn'}" in caplog.messages

    assert "Sent ntfy notification to 'http://localhost:5555'." in caplog.messages
    assert "Successfully sent message using Apprise" in caplog.messages

    assert "MQTT message received: MqttMessage(topic='frigate/cam-testdrive/goat/snapshot'" in caplog.text
    assert "Section [frigate/+/+/snapshot] matches message on frigate/cam-testdrive/goat/snapshot, processing it" in caplog.messages
    assert "Message on frigate/cam-testdrive/goat/snapshot going to store-jpeg:cam-testdrive-goat" in caplog.messages
    assert "Writing to file `/tmp/mqttwarn-frigate-cam-testdrive-goat.jpg'" in caplog.messages

    assert "Job queue has 0 items to process" in caplog.messages
    mqttc.disconnect()


@pytest.mark.parametrize("jsonfile", ["frigate-event-full.json", "frigate-event-new-good.json", "frigate-event-update-good.json"])
def test_frigate_event_with_notification(mosquitto, ntfy_service, caplog, capmqtt, jsonfile):
    """
    A full system test verifying the "Forwarding Frigate events to Ntfy" example.
    This test case submits JSON files which raise a notification.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=HERE / "frigate.ini")
    bootstrap(config=config)

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc)

    # Publish the JSON event message.
    # cat frigate-event-full.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    payload_event = open(ASSETS / jsonfile).read()
    capmqtt.publish(topic="frigate/events", payload=payload_event)

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=6)

    # Verify log output.
    assert "MQTT message received: MqttMessage(topic='frigate/events'" in caplog.text
    assert "Section [frigate/events] matches message on frigate/events, processing it" in caplog.messages
    assert "Message on frigate/events going to apprise-ntfy" in caplog.messages
    assert "Invoking service plugin for `apprise-ntfy'" in caplog.messages
    assert "Sending notification to Apprise. target=None, addresses=[]" in caplog.messages

    assert "Sent ntfy notification to 'http://localhost:5555'." in caplog.messages
    assert "Successfully sent message using Apprise" in caplog.messages

    assert "Job queue has 0 items to process" in caplog.messages
    mqttc.disconnect()


@pytest.mark.parametrize(
    "jsonfile", [
        "frigate-event-end.json",
        "frigate-event-false-positive.json",
        "frigate-event-update-samezone.json",
        "frigate-event-update-stationary.json",
        "frigate-event-new-ignored.json",
    ])
def test_frigate_event_without_notification(mosquitto, caplog, capmqtt, jsonfile):
    """
    A full system test verifying the "Forwarding Frigate events to Ntfy" example.
    This test case submits JSON files which should not raise a notification.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=HERE / "frigate.ini")
    bootstrap(config=config)

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc)

    # Publish the JSON event message.
    # cat frigate-event-full.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    payload_event = open(ASSETS / jsonfile).read()
    capmqtt.publish(topic="frigate/events", payload=payload_event)

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=6)

    # Verify log output.
    assert "MQTT message received: MqttMessage(topic='frigate/events'" in caplog.text
    assert "Section [frigate/events] matches message on frigate/events, processing it" in caplog.messages
    assert "Frigate event skipped" in caplog.text
    assert "Filter in section [frigate/events] has skipped message on frigate/events" in caplog.messages

    assert "Job queue has 0 items to process" in caplog.messages
    mqttc.disconnect()
