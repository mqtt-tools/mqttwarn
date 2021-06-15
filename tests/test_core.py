# -*- coding: utf-8 -*-
# (c) 2018-2020 The mqttwarn developers
import io
import os
import json
import tempfile

from builtins import str
import logging

import pytest

from mqttwarn.core import make_service, decode_payload
from tests import configfile_full, configfile_service_loading, configfile_no_functions, configfile_unknown_functions, \
    configfile_empty_functions
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
        core_bootstrap(configfile=configfile_full)

        # Proof that mqttwarn loaded all services properly
        assert 'Successfully loaded service "file"' in caplog.text, caplog.text
        assert 'Successfully loaded service "log"' in caplog.text, caplog.text

        assert 'Starting 1 worker threads' in caplog.text, caplog.text

        # Capturing the last message does not work. Why?
        #assert 'Job queue has 0 items to process' in caplog.text, caplog.text


def test_decode_payload_foo(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Proof that decoding an unconfigured thing yields nothing sensible.
        outcome = decode_payload(section='foo', topic='bar', payload='baz')
        assert outcome['topic'] == 'bar'
        assert outcome['payload'] == 'baz'
        assert 'Cannot decode JSON object, payload=baz' in caplog.text, caplog.text


def test_decode_payload_json(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section='foo', topic='bar', payload='{"baz": "qux"}')
        assert outcome['topic'] == 'bar'
        assert outcome['payload'] == '{"baz": "qux"}'
        assert outcome['baz'] == 'qux'


def test_decode_payload_datamap(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section='test/datamap', topic='bar', payload='{"baz": "qux"}')
        assert outcome['topic'] == 'bar'
        assert outcome['baz'] == 'qux'
        assert outcome['datamap-key'] == 'datamap-value'


def test_decode_payload_alldata(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

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
        core_bootstrap(configfile=configfile_full)

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

    tmpdir = tempfile.gettempdir()
    outputfile = os.path.join(tmpdir, 'mqttwarn-test.01')
    if os.path.exists(outputfile):
        os.unlink(outputfile)

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

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

    tmpdir = tempfile.gettempdir()
    outputfile = os.path.join(tmpdir, 'mqttwarn-test.02')
    if os.path.exists(outputfile):
        os.unlink(outputfile)

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic='test/file-2', payload=json.dumps(data))

    # Proof that the message has been written to the designated file properly.
    with io.open(outputfile, mode='rt', encoding='utf-8') as f:
        content = f.read()
        assert u'Räuber Hotzenplotz' in content, content


@pytest.mark.parametrize("configfile", [configfile_full, configfile_service_loading])
def test_plugin_module(caplog, configfile):
    """
    Check if loading a service module with dotted name works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/plugin-module', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert 'Plugin invoked' in caplog.text, caplog.text


@pytest.mark.parametrize("configfile", [configfile_full, configfile_service_loading])
def test_plugin_file(caplog, configfile):
    """
    Check if loading a service module from a file works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/plugin-file', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert 'Plugin invoked' in caplog.text, caplog.text


def test_xform_func(caplog):
    """
    Submit a message to the "log" plugin and proof
    everything gets dispatched properly.

    This time, it validates the "xform" function in the context of invoking
    a user-defined function defined through the "format" setting.
    """
    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/log-2', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "'value': 42.42" in caplog.text, caplog.text
        assert "'datamap-key': 'datamap-value'" in caplog.text, caplog.text


def test_config_no_functions(caplog):
    """
    Test a configuration file which has no `functions` setting.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile_no_functions)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/log-1', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "temperature: 42.42" in caplog.text, caplog.text


def test_config_empty_functions(caplog):
    """
    Test a configuration file which has an empty `functions` setting.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile_empty_functions)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic='test/log-1', payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "temperature: 42.42" in caplog.text, caplog.text


def test_config_bad_functions(caplog):
    """
    Test a configuration file which has no `functions` setting.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrapping the machinery with invalid path to functions file should croak.
        with pytest.raises(IOError) as excinfo:
            core_bootstrap(configfile=configfile_unknown_functions)

        error_message = str(excinfo.value)
        assert "UNKNOWN FILE REFERENCE" in error_message
        assert "not found" in error_message
