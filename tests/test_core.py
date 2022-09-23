# -*- coding: utf-8 -*-
# (c) 2018-2022 The mqttwarn developers
import io
import json
import logging
import os
import socket
import tempfile
import threading
from builtins import str
from unittest import mock
from unittest.mock import call

import pytest
from mqttwarn.core import (
    cleanup,
    decode_payload,
    make_service,
    on_connect,
    render_template,
    subscribe_forever,
)
from tests import (
    configfile_cron_invalid,
    configfile_cron_valid,
    configfile_dict_router,
    configfile_empty_functions,
    configfile_full,
    configfile_no_functions,
    configfile_no_targets,
    configfile_service_loading,
    configfile_unknown_functions,
)
from tests.util import core_bootstrap, delay, send_message


def test_make_service():
    service = make_service(name="foo")
    assert "<mqttwarn.core.Service object at" in str(service)


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

        assert "Starting 1 worker threads" in caplog.text, caplog.text

        # Capturing the last message does not work. Why?
        # assert 'Job queue has 0 items to process' in caplog.text, caplog.text


def test_decode_payload_foo(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Proof that decoding an unconfigured thing yields nothing sensible.
        outcome = decode_payload(section="foo", topic="bar", payload="baz")
        assert outcome["topic"] == "bar"
        assert outcome["payload"] == "baz"
        assert "Cannot decode JSON object, payload=baz" in caplog.text, caplog.text


def test_decode_payload_json(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section="foo", topic="bar", payload='{"baz": "qux"}')
        assert outcome["topic"] == "bar"
        assert outcome["payload"] == '{"baz": "qux"}'
        assert outcome["baz"] == "qux"


def test_decode_payload_datamap(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section="test/datamap", topic="bar", payload='{"baz": "qux"}')
        assert outcome["topic"] == "bar"
        assert outcome["baz"] == "qux"
        assert outcome["datamap-key"] == "datamap-value"


def test_decode_payload_alldata(caplog):

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Proof that decoding a valid JSON payload decodes it appropriately.
        outcome = decode_payload(section="test/alldata", topic="bar", payload='{"baz": "qux"}')
        assert outcome["topic"] == "bar"
        assert outcome["baz"] == "qux"
        assert outcome["alldata-key"] == "alldata-value"


def test_message_log(caplog):
    """
    Submit a message to the "log" plugin and proof
    everything gets dispatched properly.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic="test/log-1", payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "temperature: 42.42" in caplog.text, caplog.text


def test_message_file():
    """
    Submit a message to the "file" plugin and proof
    everything gets dispatched properly.
    """

    data = {
        "name": "temperature",
        "value": 42.42,
    }

    tmpdir = tempfile.gettempdir()
    outputfile = os.path.join(tmpdir, "mqttwarn-test.01")
    if os.path.exists(outputfile):
        os.unlink(outputfile)

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/file-1", payload=json.dumps(data))

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

    data = {"item": "Räuber Hotzenplotz"}

    tmpdir = tempfile.gettempdir()
    outputfile = os.path.join(tmpdir, "mqttwarn-test.02")
    if os.path.exists(outputfile):
        os.unlink(outputfile)

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/file-2", payload=json.dumps(data))

    # Proof that the message has been written to the designated file properly.
    with io.open(outputfile, mode="rt", encoding="utf-8") as f:
        content = f.read()
        assert "Räuber Hotzenplotz" in content, content


@pytest.mark.parametrize("configfile", [configfile_full, configfile_service_loading])
def test_plugin_module(caplog, configfile):
    """
    Check if loading a service module with dotted name works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(
            topic="test/plugin-module",
            payload='{"name": "temperature", "value": 42.42}',
        )

        # Proof that the message has been routed to the "log" plugin properly
        assert "Plugin invoked" in caplog.messages


@pytest.mark.parametrize("configfile", [configfile_full, configfile_service_loading])
def test_plugin_file(caplog, configfile):
    """
    Check if loading a service module from a file works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT
        core_bootstrap(configfile=configfile)

        # Signal mocked MQTT message to the core machinery for processing
        send_message(topic="test/plugin-file", payload='{"name": "temperature", "value": 42.42}')

        # Proof that the message has been routed to the "log" plugin properly
        assert "Plugin invoked" in caplog.messages


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
        send_message(topic="test/log-2", payload='{"name": "temperature", "value": 42.42}')

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
        send_message(topic="test/log-1", payload='{"name": "temperature", "value": 42.42}')

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
        send_message(topic="test/log-1", payload='{"name": "temperature", "value": 42.42}')

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


def test_render_template():
    tplvars = {
        "name": "foo",
        "number": 42,
        "payload": {"foo": "bar"},
        "_dthhmm": 1234567890,
    }
    response = render_template("demo.j2", tplvars)
    assert (
        response
        == """
------------------------------------------------------------
Name.................: FOO
Number...............: 42
Timestamp............: 1234567890
Original payload.....: {'foo': 'bar'}
""".strip()
    )


def test_bootstrap_with_jinja2():
    """
    Verify `jinja2` is installed.
    """

    import mqttwarn

    assert mqttwarn.core.HAVE_JINJA is True


def test_bootstrap_without_jinja2(without_jinja):
    """
    Approve that mqttwarn can also work without Jinja2.
    """

    import mqttwarn

    assert mqttwarn.core.HAVE_JINJA is False


def test_on_connect(caplog):
    for result_code in range(1, 6):
        on_connect(mosq=None, userdata=None, flags=None, result_code=result_code)
    assert caplog.record_tuples == [
        ("mqttwarn.core", 40, "Connection refused - unacceptable protocol version"),
        ("mqttwarn.core", 40, "Connection refused - identifier rejected"),
        ("mqttwarn.core", 40, "Connection refused - server unavailable"),
        ("mqttwarn.core", 40, "Connection refused - bad user name or password"),
        ("mqttwarn.core", 40, "Connection refused - not authorised"),
    ]


def test_no_targets(caplog):
    """
    Verify behavior of mqttwarn when no targets are specified.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_no_targets)

        # Signal mocked MQTT messages to the core machinery for processing.
        send_message(topic="test/template-1", payload="foobar")

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 10, "Message received on test/template-1: foobar") in caplog.record_tuples
        assert ("mqttwarn.context", 30, "Section `test/no-targets' has no targets defined") in caplog.record_tuples


def test_targets_interpolated_valid(caplog):
    """
    Verify that interpolating values into topic targets works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing.
        payload = json.dumps({"loglevel": "crit", "message": "Nur Döner macht schöner!"})
        send_message(topic="test/targets-interpolated", payload=payload)

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert (
            "mqttwarn.services.log",
            50,
            "Something crit happened! Nur Döner macht schöner!",
        ) in caplog.record_tuples


def test_targets_interpolated_unknown(caplog):
    """
    Verify that mqttwarn warns appropriately when hitting an unknown target.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing.
        payload = json.dumps({"loglevel": "unknown", "message": "foobar"})
        send_message(topic="test/targets-interpolated", payload=payload)

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 10, "New `log:unknown' job: test/targets-interpolated") in caplog.record_tuples
        assert ("mqttwarn.core", 40, "Cannot handle service=log, target=unknown") in caplog.record_tuples
        assert (
            """KeyError: "Invalid configuration: Topic 'test/targets-interpolated' """
            '''points to non-existing target 'unknown' in service 'log'"''' in caplog.text
        )


def test_targets_function_valid(caplog):
    """
    Verify that resolving the targets using a function works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing.
        send_message(topic="test/targets-function-valid", payload="foobar")

        # Proof that the message has been routed to the "log" plugin properly.
        assert (
            "mqttwarn.configuration",
            20,
            "Loading user-defined functions from tests/etc/functions_good.py",
        ) in caplog.record_tuples
        assert ("mqttwarn.core", 10, "New `log:info' job: test/targets-function-valid") in caplog.record_tuples
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert ("mqttwarn.services.log", 20, "foobar") in caplog.record_tuples


def test_targets_function_invalid(caplog):
    """
    Verify that mqttwarn warns correctly when resolving the targets using a function yields invalid results.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing.
        send_message(topic="test/targets-function-invalid", payload="foobar")

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 10, "New `log:invalid' job: test/targets-function-invalid") in caplog.record_tuples
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert (
            "mqttwarn.services.log",
            40,
            "Cannot invoke service log with level `invalid': 'invalid'",
        ) in caplog.record_tuples
        assert (
            "mqttwarn.core",
            30,
            "Notification of log for `test/targets-function-invalid' FAILED or TIMED OUT",
        ) in caplog.record_tuples


def test_targets_function_broken(caplog):
    """
    Verify that mqttwarn warns correctly when resolving the targets using a function yields invalid results.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT message to the core machinery for processing.
        send_message(topic="test/targets-function-broken", payload="foobar")

        # Proof that the message has been routed to the "log" plugin properly.
        assert (
            "mqttwarn.core",
            40,
            'Topic target definition by function "get_targets_broken" in section "test/targets-function-broken" '
            "is empty or incorrect. Should be a list. targetlist=broken, type=<class 'str'>",
        ) in caplog.record_tuples


def test_targets_dictionary_valid(caplog):
    """
    Verify that specifying the targets using a dictionary works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_dict_router)

        # Signal mocked MQTT messages to the core machinery for processing.
        send_message(topic="test/targets-dict/info", payload="foobar")
        send_message(topic="test/targets-dict/warn", payload="foobar")

        # Proof that the `info` messages have been routed to the "log" plugin properly.
        assert (
            "mqttwarn.core",
            10,
            "Section [#] matches message on test/targets-dict/info, processing it",
        ) in caplog.record_tuples
        assert ("mqttwarn.core", 10, "New `log:info' job: test/targets-dict/info") in caplog.record_tuples
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert ("mqttwarn.services.log", 20, "foobar") in caplog.record_tuples

        # Proof that the `warn` messages have been routed to the "log" plugin properly.
        assert (
            "mqttwarn.core",
            10,
            "Section [#] matches message on test/targets-dict/warn, processing it",
        ) in caplog.record_tuples
        assert ("mqttwarn.core", 10, "New `log:warn' job: test/targets-dict/warn") in caplog.record_tuples
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert ("mqttwarn.services.log", 30, "foobar") in caplog.record_tuples


def test_process_template_with_jinja(caplog):
    """
    Verify that the Jinja2 templating subsystem works.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT messages to the core machinery for processing.
        send_message(topic="test/template-1", payload=json.dumps({"name": "foobar"}))

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 10, "New `log:info' job: test/template-1") in caplog.record_tuples
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert ("mqttwarn.services.log", 20, "Name: FOOBAR") in caplog.record_tuples


def test_process_template_without_jinja(caplog, without_jinja):
    """
    Verify that mqttwarn behaves correctly when using the templating subsystem without having jinja2 installed.
    """

    with caplog.at_level(logging.DEBUG):

        # Bootstrap the core machinery without MQTT.
        core_bootstrap(configfile=configfile_full)

        # Signal mocked MQTT messages to the core machinery for processing.
        send_message(topic="test/template-1", payload=json.dumps({"name": "foobar"}))

        # Proof that the message has been routed to the "log" plugin properly.
        assert ("mqttwarn.core", 10, "New `log:info' job: test/template-1") in caplog.record_tuples
        assert ("mqttwarn.core", 30, "Templating not possible because Jinja2 is not installed") in caplog.record_tuples
        assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
        assert ("mqttwarn.services.log", 20, '{"name": "foobar"}') in caplog.record_tuples


def test_subscribe_forever_success(caplog, mocker):
    """
    Verify the `core.subscribe_forever` function.
    """

    # Adjust plumbing to speed up test case.
    mocker.patch("time.sleep", lambda _: delay(0.05))

    # Invoke `subscribe_forever` and terminate right away using `exit_flag`.
    connect = mocker.patch("mqttwarn.core.connect")
    t = threading.Thread(target=subscribe_forever)
    t.start()
    mocker.patch("mqttwarn.core.exit_flag", True)
    t.join()

    assert connect.mock_calls == [call(), call().loop_forever()]

    assert caplog.record_tuples == [
        ("mqttwarn.core", 30, "MQTT server disconnected, trying to reconnect each 5 seconds"),
    ]


def test_subscribe_forever_fails_socket_error(caplog, mocker):
    """
    Verify the `core.subscribe_forever` function correctly reports about errors.
    """

    # Adjust plumbing to speed up test case.
    mocker.patch("time.sleep", lambda _: delay(0.05))

    # Invoke `subscribe_forever` and terminate right away using `exit_flag`.
    connect = mocker.patch("mqttwarn.core.connect")
    connect.return_value = mock.MagicMock(**{"loop_forever.side_effect": socket.error("Something failed")})
    t = threading.Thread(target=subscribe_forever)
    t.start()
    mocker.patch("mqttwarn.core.exit_flag", True)
    t.join()

    assert connect.mock_calls == [call(), call().loop_forever()]

    assert caplog.record_tuples == [
        ("mqttwarn.core", 40, "Connection to MQTT broker lost: OSError(Something failed)"),
    ] or caplog.record_tuples == [
        ("mqttwarn.core", 30, "MQTT server disconnected, trying to reconnect each 5 seconds"),
    ]


def test_subscribe_forever_fails_unknown_error(caplog, mocker):
    """
    Verify the `core.subscribe_forever` function correctly reports about errors.
    """

    # Adjust plumbing to speed up test case.
    mocker.patch("time.sleep", lambda _: delay(0.05))

    # Invoke `subscribe_forever` and terminate right away using `exit_flag`.
    connect = mocker.patch("mqttwarn.core.connect")
    connect.return_value = mock.MagicMock(**{"loop_forever.side_effect": ValueError("Something failed")})
    t = threading.Thread(target=subscribe_forever)
    t.start()
    mocker.patch("mqttwarn.core.exit_flag", True)
    t.join()

    assert connect.mock_calls == [call(), call().loop_forever()]

    assert caplog.record_tuples == [
        ("mqttwarn.core", 40, "Connection to MQTT broker lost: ValueError(Something failed)"),
    ]


def test_cron_success(caplog, mocker):
    """
    Approve the `cron` subsystem.
    """

    with caplog.at_level(logging.DEBUG):

        mocker.patch("sys.exit")
        mqttc = mocker.patch("mqttwarn.core.mqttc")

        # Bootstrap the core machinery without MQTT, and shut it down again.
        core_bootstrap(configfile=configfile_cron_valid)
        cleanup()

        assert mqttc.mock_calls == [
            call.publish("clients/mqttwarn", "0", qos=0, retain=True),
            call.loop_stop(),
            call.disconnect(),
        ]

        # Proof that the cron function has been called at least once.
        assert (
            "mqttwarn.configuration",
            20,
            "Loading user-defined functions from tests/etc/functions_good.py",
        ) in caplog.record_tuples
        assert (
            "mqttwarn.configuration",
            30,
            "Expecting a list in section `defaults', key `launch' (No option 'launch' in section: 'defaults')",
        ) in caplog.record_tuples
        assert ("mqttwarn.core", 30, "No services defined") in caplog.record_tuples
        assert (
            "mqttwarn.core",
            20,
            "Scheduling periodic task 'cronfunc' to run each 0.5 seconds via [cron] section",
        ) in caplog.record_tuples
        assert ("functions_good", 20, "`cronfunc` called") in caplog.record_tuples

        assert ("mqttwarn.core", 20, "Cancelling periodic task 'cronfunc'") in caplog.record_tuples
        assert ("mqttwarn.core", 10, "Disconnecting from MQTT broker") in caplog.record_tuples
        assert ("mqttwarn.core", 20, "Waiting for queue to drain") in caplog.record_tuples
        assert ("mqttwarn.core", 10, "Exiting on signal None") in caplog.record_tuples


def test_cron_without_functions(caplog):
    """
    Verify that mqttwarn croaks when configuring a `cron` function, but no function file.
    """

    with pytest.raises(AssertionError) as ex:
        core_bootstrap(configfile=configfile_cron_invalid)
    assert ex.match("Python module must be given")
