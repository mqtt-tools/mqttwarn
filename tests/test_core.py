# -*- coding: utf-8 -*-
# (c) 2018-2020 The mqttwarn developers
import io
import os
import json

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


def test_message_log(caplog):
    """
    Submit a message to the "log" plugin and proof
    everything gets dispatched properly.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/log-1', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "temperature: 42.42" in caplog.text, caplog.text


def test_message_file():
    """
    Submit a message to the "file" plugin and proof
    everything gets dispatched properly.
    """

    data = {
        'name': 'temperature',
        'value': 42.42,
    }

    outputfile = '/tmp/mqttwarn-test.01'
    if os.path.exists(outputfile):
        os.unlink(outputfile)

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic='test/file-1', payload=json.dumps(data))

    # Proof that the message has been written to the designated file properly.
    with open(outputfile) as f:
        content = f.read()
        assert "temperature: 42.42" in content, content


def test_message_file_unicode():
    """
    Submit a message to the "file" plugin and proof
    everything gets dispatched properly.

    This time, we use special characters (umlauts)
    to proof charset encoding is also handled properly.
    """

    data = {
        'item': 'Räuber Hotzenplotz'
    }

    outputfile = '/tmp/mqttwarn-test.02'
    if os.path.exists(outputfile):
        os.unlink(outputfile)

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic='test/file-2', payload=json.dumps(data))

    # Proof that the message has been written to the designated file properly.
    with io.open(outputfile, mode='rt', encoding='utf-8') as f:
        content = f.read()
        assert u'Räuber Hotzenplotz' in content, content


def test_xform_func(caplog):
    """
    Submit a message to the "log" plugin and proof
    everything gets dispatched properly.

    This time, it validates the "xform" function in the context of invoking
    a user-defined function defined through the "format" setting.
    """
    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/log-2', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "'value': 42.42" in caplog.text, caplog.text
        assert "'datamap-key': 'datamap-value'" in caplog.text, caplog.text
