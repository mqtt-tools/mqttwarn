# -*- coding: utf-8 -*-
# (c) 2018-2023 The mqttwarn developers
import io
import json
import os
import sys
import tempfile

import pytest

from mqttwarn.core import decode_payload
from tests import configfile_full, configfile_logging_levels, configfile_service_loading
from tests.util import core_bootstrap, send_message


def test_decode_payload_foo(caplog):
    """
    Emulate and verify decoding a plain text payload using the `decode_payload` function.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Proof that decoding an unconfigured thing yields nothing sensible.
    outcome = decode_payload(section="foo", topic="bar", payload="baz")
    assert outcome["topic"] == "bar"
    assert outcome["payload"] == "baz"
    assert "Decoding JSON failed: Expecting value: line 1 column 1 (char 0). payload=baz" in caplog.text, caplog.text


def test_decode_payload_json(caplog):
    """
    Emulate and verify decoding a JSON payload using the `decode_payload` function.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Proof that decoding a valid JSON payload decodes it appropriately.
    outcome = decode_payload(section="foo", topic="bar", payload='{"baz": "qux"}')
    assert outcome["topic"] == "bar"
    assert outcome["payload"] == '{"baz": "qux"}'
    assert outcome["baz"] == "qux"


@pytest.mark.parametrize("section", ["test/datamap-1", "test/datamap-2"])
def test_decode_payload_datamap(section, caplog):
    """
    Verify decoding a JSON payload when there is a `datamap` function in place.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Proof that decoding a valid JSON payload decodes it appropriately.
    outcome = decode_payload(section=section, topic="bar", payload='{"baz": "qux"}')
    assert outcome["topic"] == "bar"
    assert outcome["baz"] == "qux"
    assert outcome["datamap-key"] == "datamap-value"


def test_decode_payload_alldata(caplog):
    """
    Verify decoding a JSON payload when there is an `alldata` function in place.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Proof that decoding a valid JSON payload decodes it appropriately.
    outcome = decode_payload(section="test/alldata", topic="bar", payload='{"baz": "qux"}')
    assert outcome["topic"] == "bar"
    assert outcome["baz"] == "qux"
    assert outcome["alldata-key"] == "alldata-value"


@pytest.mark.parametrize("topic", ["test/filter-1", "test/filter-2"])
def test_filter_valid_accept(topic, caplog):
    """
    Verify that applying a `filter` function works. The message will get accepted based on the message payload.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic=topic, payload="accept")

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 10, f"Message received on {topic}: accept") in caplog.record_tuples
    assert ("mqttwarn.core", 10, f"Section [{topic}] matches message on {topic}, processing it") in caplog.record_tuples

    assert ("mqttwarn.core", 10, f"New `log:info' job: {topic}") in caplog.record_tuples
    assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
    assert ("mqttwarn.services.log", 20, "accept") in caplog.record_tuples


@pytest.mark.parametrize("topic", ["test/filter-1", "test/filter-2"])
def test_filter_valid_reject(topic, caplog):
    """
    Verify that applying a `filter` function works. The message will get rejected based on the message payload.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic=topic, payload="reject")

    # Proof that the message has been properly rejected by the `filter` function.
    assert ("mqttwarn.core", 10, f"Message received on {topic}: reject") in caplog.record_tuples
    assert ("mqttwarn.core", 10, f"Section [{topic}] matches message on {topic}, processing it") in caplog.record_tuples

    assert ("mqttwarn.core", 20, f"Filter in section [{topic}] has skipped message on {topic}") in caplog.record_tuples


def test_message_log(caplog):
    """
    Submit a message to the `log` plugin and proof everything gets dispatched properly.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/log-1", payload='{"name": "temperature", "value": 42.42}')

    # Proof that the message has been routed to the `log` plugin properly.
    assert "temperature: 42.42" in caplog.text, caplog.text


@pytest.mark.parametrize("topic", ["test/filter-1"])
def test_filter_valid_reject_filteredmessagesloglevel(mocker, topic, caplog):
    """
    Verify that setting the filteredmessagesloglevel config option changes the log level
    of the "Filter in section" message.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_logging_levels)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic=topic, payload="reject")

    # Proof that the message has been properly rejected by the `filter` function.
    assert ("mqttwarn.core", 10, f"Message received on {topic}: reject") in caplog.record_tuples
    assert ("mqttwarn.core", 10, f"Section [{topic}] matches message on {topic}, processing it") in caplog.record_tuples

    assert ("mqttwarn.core", 10, f"Filter in section [{topic}] has skipped message on {topic}") in caplog.record_tuples


def test_message_log_skip_retained(mocker, caplog):
    """
    Submit a message with retained flag and check if it will get discarded when the
    `skipretained` setting is enabled.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Adjust `skipretained` configuration setting.
    mocker.patch("mqttwarn.core.cf.skipretained", True)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/log-1", payload='{"name": "temperature", "value": 42.42}', retain=True)

    # Verify that the message has been rejected.
    assert ("mqttwarn.core", 10, "Skipping retained message on test/log-1") in caplog.record_tuples


def test_message_file():
    """
    Submit a message to the `file` plugin and proof everything gets dispatched properly.
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
    Submit a message to the `file` plugin and proof everything gets dispatched properly.

    This time, we use special characters (umlauts) to proof charset encoding is also handled properly.
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

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(
        topic="test/plugin-module",
        payload='{"name": "temperature", "value": 42.42}',
    )

    # Verify that the module has been loaded.
    assert "Plugin invoked" in caplog.messages


@pytest.mark.parametrize("configfile", [configfile_full, configfile_service_loading])
def test_plugin_file(caplog, configfile):
    """
    Check if loading a service module from a file works.
    """

    # Bootstrap the core machinery without MQTT
    core_bootstrap(configfile=configfile)

    # Signal mocked MQTT message to the core machinery for processing
    send_message(topic="test/plugin-file", payload='{"name": "temperature", "value": 42.42}')

    # Verify that the module has been loaded.
    assert "Plugin invoked" in caplog.messages


def test_xform_func_success(caplog):
    """
    Submit a message to the `log` plugin and proof everything gets dispatched properly.

    This time, it validates the `xform` function in the context of invoking
    a user-defined function defined through the `format` setting.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/log-2", payload='{"name": "temperature", "value": 42.42}')

    # Proof that the message has been dispatched properly.
    assert "'value': 42.42" in caplog.text, caplog.text
    assert "'xform-key': 'xform-value'" in caplog.text, caplog.text


def test_xform_func_failure(caplog):
    """
    Submit a message to the `log` plugin and proof everything gets dispatched properly.

    This time, it validates the `xform` function in the context of invoking
    a user-defined function defined through the `format` setting.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/log-unknown-func", payload='{"name": "temperature", "value": 42.42}')

    # Proof that the message has been dispatched properly.
    assert "Invoking function failed: unknown_func()" in caplog.messages


def test_no_targets(tmp_ini, caplog):
    """
    Verify behavior of mqttwarn when no targets are specified.
    """

    # Bootstrap the core machinery without MQTT.
    tmp_ini.write_text("[test/no-targets]")
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/template-1", payload="foobar")

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 10, "Message received on test/template-1: foobar") in caplog.record_tuples
    assert ("mqttwarn.context", 30, "Section `test/no-targets' has no targets defined") in caplog.record_tuples


def test_targets_interpolated_valid(caplog):
    """
    Verify that interpolating values into topic targets works.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    payload = json.dumps({"loglevel": "crit", "message": "Nur Döner macht schöner!"})
    send_message(topic="test/targets-interpolated", payload=payload)

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
    assert ("mqttwarn.services.log", 50, "Something crit happened! Nur Döner macht schöner!") in caplog.record_tuples


def test_targets_interpolated_unknown(caplog):
    """
    Verify that mqttwarn warns appropriately when hitting an unknown target.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    payload = json.dumps({"loglevel": "unknown", "message": "foobar"})
    send_message(topic="test/targets-interpolated", payload=payload)

    # Proof that the message has been routed to the `log` plugin properly.
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

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/targets-function-valid", payload="foobar")

    # Proof that the message has been routed to the `log` plugin properly.
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

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/targets-function-invalid", payload="foobar")

    # Proof that the message has been routed to the `log` plugin properly.
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
        "Notification failed or timed out. service=log, topic=test/targets-function-invalid",
    ) in caplog.record_tuples


def test_targets_function_broken(caplog):
    """
    Verify that mqttwarn warns correctly when resolving the targets using a function yields invalid results.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/targets-function-broken", payload="foobar")

    # Proof that the message has been routed to the `log` plugin properly.
    assert (
        "mqttwarn.core",
        40,
        'Topic target definition by function "get_targets_broken" in section "test/targets-function-broken" '
        "is empty or incorrect. Should be a list. targetlist=broken, type=<class 'str'>",
    ) in caplog.record_tuples


def test_targets_function_error(caplog):
    """
    Verify that mqttwarn warns correctly when resolving the targets using a function raises an exception.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/targets-function-error", payload="foobar")

    # Proof that the error appears in the log output.
    assert (
        """Error invoking topic targets function "get_targets_error" defined in """
        """section "test/targets-function-error": ValueError('Something failed'""" in caplog.text
    )
    assert (
        'Topic target definition by function "get_targets_error" in section '
        '"test/targets-function-error" is empty or incorrect. Should be a list.' in caplog.text
    )


def test_targets_dictionary(tmp_ini, caplog):
    """
    Verify that specifying the targets using a dictionary works as expected.
    """

    tmp_ini.write_text(
        """
[defaults]
launch    = log

[config:log]
targets = {
    'debug'  : [ 'debug' ],
    'info'   : [ 'info' ],
    'warn'   : [ 'warn' ],
    'crit'   : [ 'crit' ],
    'error'  : [ 'error' ]
  }

[#]
targets = {
  'test/targets-dict/info': 'log:info',
  'test/targets-dict/warn': [ 'log:warn' ],
  }
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/targets-dict/info", payload="foobar")
    send_message(topic="test/targets-dict/warn", payload="foobar")

    # Proof that the `info` messages have been routed to the `log` plugin properly.
    assert (
        "mqttwarn.core",
        10,
        "Section [#] matches message on test/targets-dict/info, processing it",
    ) in caplog.record_tuples
    assert ("mqttwarn.core", 10, "New `log:info' job: test/targets-dict/info") in caplog.record_tuples
    assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
    assert ("mqttwarn.services.log", 20, "foobar") in caplog.record_tuples

    # Proof that the `warn` messages have been routed to the `log` plugin properly.
    assert (
        "mqttwarn.core",
        10,
        "Section [#] matches message on test/targets-dict/warn, processing it",
    ) in caplog.record_tuples
    assert ("mqttwarn.core", 10, "New `log:warn' job: test/targets-dict/warn") in caplog.record_tuples
    assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
    assert ("mqttwarn.services.log", 30, "foobar") in caplog.record_tuples


def test_targets_service_targets(tmp_ini, caplog):
    """
    Verify dispatching when `targets` does not address a specific slot, but instead
    multiplexes to all `targets` within `[config:log]`. For doing that, it needs to
    look up all targets using `context.get_service_targets`.
    """
    tmp_ini.write_text(
        """
[defaults]
launch = log

[config:log]
targets = {
    'debug'  : [ 'debug' ],
    'info'   : [ 'info' ],
    'warn'   : [ 'warn' ],
  }

[test/target-service-targets]
targets = log
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/target-service-targets", payload="foobar")

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 20, 'Successfully loaded service "log"') in caplog.record_tuples
    assert ("mqttwarn.core", 10, "Message on test/target-service-targets going to log") in caplog.record_tuples
    assert ("mqttwarn.core", 10, "New `log:debug' job: test/target-service-targets") in caplog.record_tuples
    assert ("mqttwarn.core", 10, "New `log:info' job: test/target-service-targets") in caplog.record_tuples
    assert ("mqttwarn.core", 10, "New `log:warn' job: test/target-service-targets") in caplog.record_tuples
    assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
    # assert ("mqttwarn.core", 10, "Job queue has 2 items to process") in caplog.record_tuples
    # assert ("mqttwarn.core", 10, "Job queue has 1 items to process") in caplog.record_tuples
    assert ("mqttwarn.core", 10, "Job queue has 0 items to process") in caplog.record_tuples


def test_targets_service_non_existing_target(tmp_ini, caplog):
    """
    The specified target, `log:info`, does not exist on the service `[config:log]`.
    """
    tmp_ini.write_text(
        """
[defaults]
launch = log

[config:log]
targets = bar

[test/target-invalid]
targets = log:info
format = {name}: {value}
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/target-invalid", payload=json.dumps({"name": "foobar"}))

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 20, 'Successfully loaded service "log"') in caplog.record_tuples
    assert ("mqttwarn.core", 10, "New `log:info' job: test/target-invalid") in caplog.record_tuples
    assert ("mqttwarn.core", 40, "Cannot handle service=log, target=info") in caplog.record_tuples
    assert (
        "Invalid configuration: Topic 'test/target-invalid' points to non-existing target 'info' in service 'log'"
        in caplog.text
    )


def test_targets_dict_nomatch(tmp_ini, caplog):
    """
    The specified target topic match spec, `{'abc': 'def'}`, does not match `test/target-invalid`.
    """
    tmp_ini.write_text(
        """
[defaults]
launch = log

[config:log]
targets = bar

[test/target-invalid]
targets = {'abc': 'def'}
format = {name}: {value}
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/target-invalid", payload=json.dumps({"name": "foobar"}))

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 20, 'Successfully loaded service "log"') in caplog.record_tuples
    assert (
        "mqttwarn.core",
        10,
        "Dispatcher definition does not contain matching topic/target pair in section [test/target-invalid]",
    ) in caplog.record_tuples


def test_targets_service_unknown(tmp_ini, caplog):
    """
    There is no service named `foo`. `mqttwarn` should warn correspondingly.
    """
    tmp_ini.write_text(
        """
[test/target-unknown]
targets = foo:info
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/target-unknown", payload=json.dumps({"name": "foobar"}))

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 10, "Message on test/target-unknown going to foo:info") in caplog.record_tuples
    assert "Invalid configuration: Topic 'test/target-unknown' points to non-existing service 'foo'" in caplog.text


def test_targets_service_invalid(tmp_ini, caplog):
    """
    Topic targets like `foo:bar:baz` can not be decoded. `mqttwarn` should emit a corresponding log message.
    """
    tmp_ini.write_text(
        """
[test/target-invalid]
targets = foo:bar:baz
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/target-invalid", payload=json.dumps({"name": "foobar"}))

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 10, "Message on test/target-invalid going to foo:bar:baz") in caplog.record_tuples
    assert (
        "mqttwarn.core",
        40,
        "Invalid topic target: foo:bar:baz. Should be 'service:target'.",
    ) in caplog.record_tuples


def test_targets_service_interpolation_success(tmp_ini, caplog):
    """
    Verify interpolating transformation data values into topic targets works.
    """
    tmp_ini.write_text(
        """
[test/target-interpolate]
targets = example:{name}
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/target-interpolate", payload=json.dumps({"name": "foobar"}))


@pytest.mark.skipif(sys.version_info < (3, 7), reason="This test only works on Python >= 3.7")
def test_targets_service_interpolation_failure(tmp_ini, caplog):
    """
    When interpolating transformation data values into topic targets, and it fails,
    a meaningful log message should have been generated.
    """
    tmp_ini.write_text(
        """
[test/target-interpolate]
targets = example:{name}
    """
    )

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=tmp_ini)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/target-interpolate", payload="foobar")

    # Verify the log message indicating the failure.
    messages = list(map(lambda x: x.msg, caplog.records))
    assert (
        "Interpolating transformation data into topic target 'example:{name}' failed. Reason: KeyError('name'). "
        "section=test/target-interpolate, topic=test/target-interpolate, payload=foobar, data=%s" in messages
    )


def test_template_with_jinja(caplog):
    """
    Verify that the Jinja2 templating subsystem works.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/template-1", payload=json.dumps({"name": "foobar"}))

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 10, "New `log:info' job: test/template-1") in caplog.record_tuples
    assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
    assert ("mqttwarn.services.log", 20, "Name: FOOBAR") in caplog.record_tuples


def test_template_without_jinja(caplog, without_jinja):
    """
    Verify that mqttwarn behaves correctly when using the templating subsystem without having Jinja2 installed.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Signal mocked MQTT messages to the core machinery for processing.
    send_message(topic="test/template-1", payload=json.dumps({"name": "foobar"}))

    # Proof that the message has been routed to the `log` plugin properly.
    assert ("mqttwarn.core", 10, "New `log:info' job: test/template-1") in caplog.record_tuples
    assert ("mqttwarn.core", 30, "Templating not possible because Jinja2 is not installed") in caplog.record_tuples
    assert ("mqttwarn.core", 20, "Invoking service plugin for `log'") in caplog.record_tuples
    assert ("mqttwarn.services.log", 20, '{"name": "foobar"}') in caplog.record_tuples
