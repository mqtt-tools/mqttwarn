# -*- coding: utf-8 -*-
# (c) 2018 The mqttwarn developers
import logging

from mqttwarn.core import make_service
from tests import configfile
from tests.util import core_bootstrap, send_message


def test_make_service():
    service = make_service(name='foo')
    assert '<mqttwarn.core.Service object at' in str(service)


def test_bootstrap(caplog):
    """
    Bootstrap the core machinery without MQTT
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Proof that mqttwarn loaded all services properly
        assert 'Successfully loaded service "file"' in caplog.text, caplog.text
        assert 'Successfully loaded service "log"' in caplog.text, caplog.text

        assert 'Starting 1 worker threads' in caplog.text, caplog.text

        # Capturing the last message does not work. Why?
        #assert 'Job queue has 0 items to process' in caplog.text, caplog.text


def test_on_message(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/log-1', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "u'temperature: 42.42" in caplog.text, caplog.text
