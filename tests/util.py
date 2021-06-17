# -*- coding: utf-8 -*-
# (c) 2018-2021 The mqttwarn developers
import time
from dataclasses import dataclass
from typing import Dict, Union, List

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
    if payload is not None:
        message.payload = payload.encode('utf-8')

    # Signal the message to the machinery
    on_message(None, None, message)

    # Give the machinery some time to process the message
    time.sleep(0.05)


@dataclass
class ProcessorItem:
    """
    A surrogate processor item for feeding into service handlers.
    """

    service: str = None
    target: str = None
    config: Dict = None
    addrs: List[str] = None
    topic: str = None
    title: str = None
    message: Union[str, bytes] = None
    data: Dict = None
