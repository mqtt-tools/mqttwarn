# -*- coding: utf-8 -*-
# (c) 2023 The mqttwarn developers
"""
Software test accompanying "Forwarding Frigate events to ntfy" example.
Full system test verifying mqttwarn end-to-end, using an MQTT broker, and an ntfy instance.
"""
import os
import subprocess
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


@pytest.fixture(scope="function", autouse=True)
def reset_filestore():
    """
    Make sure there are no temporary spool files around before starting each test case.
    """
    for filepath in Path("/tmp").glob("mqttwarn-frigate-*"):
        os.unlink(filepath)


def test_frigate_with_attachment(mosquitto, ntfy_service, caplog, capmqtt):
    """
    A full system test verifying the "Forwarding Frigate events to ntfy" example.
    This test case submits the `frigate-event-full.json` file as MQTT event message.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=HERE / "frigate.ini")
    bootstrap(config=config)

    # Get image payload.
    payload_image = get_goat_image()

    # Add MQTT.
    mqttc = connect()

    # Make mqttwarn run the subscription to the broker.
    mqtt_process(mqttc)

    # Publish the JSON event message.
    # cat frigate-event-new-good.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    payload_event = open(ASSETS / "frigate-event-full.json").read()
    capmqtt.publish(topic="frigate/events", payload=payload_event)

    # Publish the snapshot image.
    # mosquitto_pub -f goat.png -t 'frigate/cam-testdrive/goat/snapshot'
    capmqtt.publish(topic="frigate/cam-testdrive/goat/snapshot", payload=payload_image)

    # Make mqttwarn receive and process the message.
    mqtt_process(mqttc, loops=8)

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
        "'Title': '=?utf-8?q?goat_entered_lawn_at_2023-04-06_14=3A31=3A46=2E638857+00=3A00?=', "
        "'Message': '=?utf-8?q?goat_was_in_barn_before?=', "
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

    # Verify notification was properly received by ntfy.
    url = "http://localhost:5555/frigate-testdrive/json?poll=1&since=5s"
    response = requests.get(url)
    data = response.json()
    del data["id"]
    del data["time"]
    del data["expires"]
    del data["attachment"]["url"]
    del data["attachment"]["expires"]
    assert data == {
        "event": "message",
        "topic": "frigate-testdrive",
        "title": "goat entered lawn at 2023-04-06 14:31:46.638857+00:00",
        "message": "goat was in barn before",
        "click": "https://httpbin.org/anything?camera=cam-testdrive&label=goat&zone=lawn",
        "attachment": {
           "name": "mqttwarn-frigate-cam-testdrive-goat.png",
           "size": 283595,
           "type": "image/png",
        },
    }


@pytest.mark.parametrize(
    "jsonfile", ["frigate-event-full.json", "frigate-event-new-good.json", "frigate-event-update-good.json"]
)
def test_frigate_with_notification(mosquitto, ntfy_service, caplog, capmqtt, jsonfile):
    """
    A full system test verifying the "Forwarding Frigate events to ntfy" example.
    This test case submits JSON files which trigger a notification.
    """

    # Bootstrap the core machinery without MQTT.
    config = load_configuration(configfile=HERE / "frigate.ini")
    turn_off_retries(config)
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
    assert "Message on frigate/events going to ntfy:test" in caplog.messages
    assert "Invoking service plugin for `ntfy'" in caplog.messages
    assert "Body:    b'goat was in barn before'" in caplog.messages
    assert (
        "Headers: {"
        "'Click': 'https://httpbin.org/anything?camera=cam-testdrive&label=goat&zone=lawn', "
        "'Title': '=?utf-8?q?goat_entered_lawn_at_2023-04-06_14=3A31=3A46=2E638857+00=3A00?='}" in caplog.messages
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
def test_frigate_without_notification(mosquitto, caplog, capmqtt, jsonfile):
    """
    A full system test verifying the "Forwarding Frigate events to ntfy" example.
    This test case submits JSON files which should not trigger a notification.
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


def get_goat_image() -> bytes:
    """
    Get an image of a Changthangi goat.
    """
    return requests.get(
        "https://user-images.githubusercontent.com/453543/231550862-5a64ac7c-bdfa-4509-86b8-b1a770899647.png"
    ).content


def turn_off_retries(config):
    """
    For test cases which do not aim to submit any attachments, adjust the configuration
    to not wait for it to appear. Otherwise, it would take too long, and the verification
    would fail.
    """
    targets = config.getdict("config:ntfy", "targets")
    targets["test"]["__settings__"]["file_retry_tries"] = None
    config.set("config:ntfy", "targets", targets)
