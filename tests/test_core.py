# -*- coding: utf-8 -*-
# (c) 2018 The mqttwarn developers
from builtins import str
import logging

from mqttwarn.core import make_service, decode_payload
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


def test_decode_payload_foo(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile)

        # Proof that decoding an unconfigured thing yields nothing sensible.
        outcome = decode_payload(section='foo', topic='bar', payload='baz')
        assert outcome['topic'] == 'bar'
        assert outcome['payload'] == 'baz'
        assert 'Cannot decode JSON object, payload=baz' in caplog.text, caplog.text


def test_decode_payload_json(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section='foo', topic='bar', payload='{"baz": "qux"}')
        assert outcome['topic'] == 'bar'
        assert outcome['payload'] == '{"baz": "qux"}'
        assert outcome['baz'] == 'qux'


def test_decode_payload_datamap(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section='test/datamap', topic='bar', payload='{"baz": "qux"}')
        assert outcome['topic'] == 'bar'
        assert outcome['baz'] == 'qux'
        assert outcome['datamap-key'] == 'datamap-value'


def test_decode_payload_alldata(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section='test/alldata', topic='bar', payload='{"baz": "qux"}')
        assert outcome['topic'] == 'bar'
        assert outcome['baz'] == 'qux'
        assert outcome['alldata-key'] == 'alldata-value'


def test_message_basic(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/log-1', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "u'temperature: 42.42" in caplog.text, caplog.text
