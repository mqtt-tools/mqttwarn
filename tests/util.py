# -*- coding: utf-8 -*-
# (c) 2018-2021 The mqttwarn developers
import shlex
import threading
import time
from unittest.mock import patch

import paho
from paho.mqtt.client import MQTTMessage

import mqttwarn
from mqttwarn.commands import run as run_command
from mqttwarn.configuration import load_configuration
from mqttwarn.core import bootstrap, load_services, on_message, start_workers


def core_bootstrap(configfile=None):
    """
    Bootstrap the core machinery without MQTT.
    """

    # If mqttwarn was already invoked beforehand, reset "exit flag".
    # TODO: Get rid of global variables.
    mqttwarn.core.exit_flag = False

    # Load configuration file
    config = load_configuration(configfile)

    # Bootstrap mqttwarn.core
    bootstrap(config=config, scriptname="testdrive")

    # Load services
    services = config.getlist("defaults", "launch")
    load_services(services)

    # Launch worker threads to operate on queue
    start_workers()


def send_message(topic=None, payload=None, retain=False):

    # Mock an instance of an Eclipse Paho MQTTMessage
    message = MQTTMessage(mid=42, topic=topic.encode("utf-8"))
    if payload is not None:
        message.payload = payload.encode("utf-8")
    if retain:
        message.retain = True

    # Signal the message to the machinery
    on_message(None, None, message)

    # Give the machinery some time to process the message
    delay()


def delay(seconds=0.075):
    """
    Wait for designated number of seconds.
    """
    threading.Event().wait(seconds)


def mqtt_process(mqttc: paho.mqtt.client.Client, loops=2):
    """
    Process network events for Paho MQTT client library. Wait a bit before and after.
    """
    delay()
    for _ in range(loops):
        mqttc.loop(max_packets=10)
        time.sleep(0.01)
    delay()


def invoke_command(capfd, command):
    if not isinstance(command, list):
        command = shlex.split(command)
    with patch("sys.argv", command):
        run_command()
    output = capfd.readouterr()
    return output.out, output.err


class FakeResponse:
    """
    https://www.mitchellcurrie.com/blog-post/python-mock-unittesting/
    """

    status: int
    data: bytes

    def __init__(self, *, data: bytes):
        self.data = data

    def read(self):
        self.status = 200 if self.data is not None else 404
        return self.data

    def close(self):
        pass
