# -*- coding: utf-8 -*-
# (c) 2018 The mqttwarn developers
import time
from paho.mqtt.client import MQTTMessage

from mqttwarn.configuration import load_configuration
from mqttwarn.core import bootstrap, on_message, load_services, start_workers


def core_bootstrap(configfile=None):
    """
    Bootstrap the core machinery without MQTT
    """

    # Load configuration file
    config = load_configuration(configfile)

    # Bootstrap mqttwarn.core
    bootstrap(config=config, scriptname='testdrive')

    # Load services
    services = config.getlist('defaults', 'launch')
    load_services(services)

    # Launch worker threads to operate on queue
    start_workers()


def send_message(topic=None, payload=None):

    # Mock an instance of an Eclipse Paho MQTTMessage
    message = MQTTMessage(mid=42, topic=topic.encode('utf-8'))
    message.payload = payload

    # Signal the message to the machinery
    on_message(None, None, message)

    # Give the machinery some time to process the message
    time.sleep(0.05)
