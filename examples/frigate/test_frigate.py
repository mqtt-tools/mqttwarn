# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
"""
Software test accompanying "Forwarding Frigate events to ntfy" example.
Full system test verifying mqttwarn end-to-end, using an MQTT broker, and an ntfy instance.
"""
import os
import sys
from pathlib import Path

import pytest
import requests

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
    A full system test verifying the "Forwarding Frigate events to ntfy" example.
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
    # mosquitto_pub -f goat.png -t 'frigate/cam-testdrive/goat/snapshot'
    payload_image = get_goat_image()
    capmqtt.publish(topic="frigate/cam-testdrive/goat/snapshot", payload=payload_image)

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=4)

    # Verify log output.
    assert 'Successfully loaded service "ntfy"' in caplog.messages
    assert 'Successfully loaded service "store-image"' in caplog.messages

    assert "Subscribing to frigate/events (qos=0)" in caplog.messages
    assert "Subscribing to frigate/+/+/snapshot (qos=0)" in caplog.messages

    assert "MQTT message received: MqttMessage(topic='frigate/events'" in caplog.text
    assert "Section [frigate/events] matches message on frigate/events, processing it" in caplog.messages
    assert "Message on frigate/events going to ntfy:test" in caplog.messages
    assert "Invoking service plugin for `ntfy'" in caplog.messages
    assert (
        "Headers: {"
        "'Click': 'https://httpbin.org/anything?camera=cam-testdrive&label=goat&zone=lawn', "
        "'Title': 'goat entered lawn at 2023-04-06 14:31:46.638857+00:00', "
        "'Message': 'goat was in barn before', "
        "'Filename': 'mqttwarn-frigate-cam-testdrive-goat.png'}" in caplog.messages
    )
    assert (
        "Sending notification to ntfy. target=test, options={"
        "'url': 'http://username:password@localhost:5555/frigate-testdrive', "
        "'file': '/tmp/mqttwarn-frigate-{camera}-{label}.png', "
        "'click': 'https://httpbin.org/anything?camera={event.camera}&label={event.label}&zone={event.entered_zones[0]}'}"
        in caplog.messages
    )

    # assert "Sent ntfy notification to 'http://localhost:5555'." in caplog.messages
    assert "Successfully sent message using ntfy" in caplog.messages

    assert "MQTT message received: MqttMessage(topic='frigate/cam-testdrive/goat/snapshot'" in caplog.text
    assert (
        "Section [frigate/+/+/snapshot] matches message on frigate/cam-testdrive/goat/snapshot, processing it"
        in caplog.messages
    )
    assert "Message on frigate/cam-testdrive/goat/snapshot going to store-image:cam-testdrive-goat" in caplog.messages
    assert "Writing to file `/tmp/mqttwarn-frigate-cam-testdrive-goat.png'" in caplog.messages

    assert "Job queue has 0 items to process" in caplog.messages
    mqttc.disconnect()


@pytest.mark.parametrize(
    "jsonfile", ["frigate-event-full.json", "frigate-event-new-good.json", "frigate-event-update-good.json"]
)
def test_frigate_event_with_notification(mosquitto, ntfy_service, caplog, capmqtt, jsonfile):
    """
    A full system test verifying the "Forwarding Frigate events to ntfy" example.
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
    mqtt_process(mqttc, loops=2)

    # Verify log output.
    assert "MQTT message received: MqttMessage(topic='frigate/events'" in caplog.text
    assert "Section [frigate/events] matches message on frigate/events, processing it" in caplog.messages
    assert "Message on frigate/events going to ntfy:test" in caplog.messages
    assert "Invoking service plugin for `ntfy'" in caplog.messages
    assert (
        "Headers: {"
        "'Click': 'https://httpbin.org/anything?camera=cam-testdrive&label=goat&zone=lawn', "
        "'Title': 'goat entered lawn at 2023-04-06 14:31:46.638857+00:00', "
        "'Message': 'goat was in barn before', "
        "'Filename': 'mqttwarn-frigate-cam-testdrive-goat.png'}" in caplog.messages
    )

    # assert "Sent ntfy notification to 'http://localhost:5555'." in caplog.messages
    assert "Successfully sent message using ntfy" in caplog.messages

    assert "Job queue has 0 items to process" in caplog.messages
    mqttc.disconnect()


@pytest.mark.parametrize(
    "jsonfile",
    [
        "frigate-event-end.json",
        "frigate-event-false-positive.json",
        "frigate-event-update-samezone.json",
        "frigate-event-update-stationary.json",
        "frigate-event-new-ignored.json",
    ],
)
def test_frigate_event_without_notification(mosquitto, caplog, capmqtt, jsonfile):
    """
    A full system test verifying the "Forwarding Frigate events to ntfy" example.
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
    mqtt_process(mqttc, loops=3)

    # Verify log output.
    assert "MQTT message received: MqttMessage(topic='frigate/events'" in caplog.text
    assert "Section [frigate/events] matches message on frigate/events, processing it" in caplog.messages
    assert "Frigate event skipped" in caplog.text
    assert "Filter in section [frigate/events] has skipped message on frigate/events" in caplog.messages

    assert "Job queue has 0 items to process" in caplog.messages
    mqttc.disconnect()


def get_goat_image() -> bytes:
    """
    Get an image of a Changthangi goat.
    """
    return requests.get(
        "https://user-images.githubusercontent.com/453543/231550862-5a64ac7c-bdfa-4509-86b8-b1a770899647.png"
    ).content
