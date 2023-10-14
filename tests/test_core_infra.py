# -*- coding: utf-8 -*-
# (c) 2018-2023 The mqttwarn developers
import configparser
import socket
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
from unittest.mock import Mock, call

import pytest
from paho.mqtt.client import Client as MqttClient
from paho.mqtt.client import MQTTMessage

from mqttwarn.configuration import Config
from mqttwarn.context import RuntimeContext
from mqttwarn.core import (
    bootstrap,
    cleanup,
    connect,
    load_services,
    on_connect,
    on_disconnect,
    on_message,
    publish_status_information,
    render_template,
    run_plugin,
    send_failover,
    subscribe_forever,
    xform,
)
from tests import configfile_empty_functions, configfile_full, configfile_no_functions
from tests.util import core_bootstrap, delay, send_message


def test_bootstrap_success(caplog):
    """
    Verify the test utility bootstrapping function `core_bootstrap`.
    It will bootstrap the core machinery without MQTT.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_full)

    # Proof that mqttwarn loaded all services properly
    assert 'Successfully loaded service "file"' in caplog.messages
    assert 'Successfully loaded service "log"' in caplog.messages

    assert "Starting 1 worker threads" in caplog.messages

    # Capturing the last message does not work. Why?
    # assert 'Job queue has 0 items to process' in caplog.messages


def test_config_no_functions(caplog):
    """
    Test a configuration file which has no `functions` setting.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_no_functions)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/log-1", payload='{"name": "temperature", "value": 42.42}')

    # Proof that the message has been dispatched properly.
    assert "temperature: 42.42" in caplog.text, caplog.text


def test_config_empty_functions(caplog):
    """
    Test a configuration file which has an empty `functions` setting.
    """

    # Bootstrap the core machinery without MQTT.
    core_bootstrap(configfile=configfile_empty_functions)

    # Signal mocked MQTT message to the core machinery for processing.
    send_message(topic="test/log-1", payload='{"name": "temperature", "value": 42.42}')

    # Proof that the message has been dispatched properly.
    assert "temperature: 42.42" in caplog.text, caplog.text


def test_config_functions_file_not_found(tmp_ini, caplog):
    """
    Test a configuration file which references a bad `functions` file.
    Bootstrapping the machinery with an invalid path to a `functions` file should croak.
    """

    tmp_ini.write_text(
        """
[defaults]

; This is an *invalid* `functions` setting.
functions = 'UNKNOWN FILE REFERENCE'
    """
    )

    with pytest.raises(IOError) as excinfo:
        core_bootstrap(configfile=tmp_ini)

    error_message = str(excinfo.value)
    assert "UNKNOWN FILE REFERENCE" in error_message
    assert "not found" in error_message


def test_render_template():
    """
    Render a template with Jinja2.
    """
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
    Verify the `jinja2` package is installed.
    """

    import mqttwarn

    assert mqttwarn.core.HAVE_JINJA is True


def test_bootstrap_without_jinja2(without_jinja):
    """
    Approve that mqttwarn can also work without Jinja2.
    """

    import mqttwarn

    assert mqttwarn.core.HAVE_JINJA is False


def test_connect_basic_success(mocker, caplog):
    """
    Verify the `connect()` function succeeds.
    """

    # Use a real configuration object.
    config = Config(defaults={"clientid": "testdrive"})
    mocker.patch("mqttwarn.core.cf", config)

    # Use mocked MQTT client and mqttwarn context instances.
    mqtt_client: Mock = mocker.patch("paho.mqtt.client.Client")
    mqttwarn_context: Mock = mocker.patch("mqttwarn.core.context")

    # Run the `connect` function to completion.
    connect()

    assert mqtt_client.mock_calls == [
        call("testdrive", clean_session=False, protocol=3),
        call().connect("localhost", 1883, 60),
    ]
    assert mqttwarn_context.mock_calls == []

    assert (
        "mqttwarn.configuration",
        30,
        "Expecting a list in section `defaults', key `launch' (No section: 'defaults')",
    ) in caplog.record_tuples
    assert ("mqttwarn.core", 30, "No services defined") in caplog.record_tuples


def test_connect_auth_success(mocker, caplog):
    """
    Verify the `connect()` function does the right thing when requesting MQTT broker authentication.
    """

    # Use a real configuration object.
    config = Config(defaults={"clientid": "testdrive"})
    config.username = "foo"
    config.password = None
    mocker.patch("mqttwarn.core.cf", config)

    # Use mocked MQTT client and mqttwarn context instances.
    mqtt_client: Mock = mocker.patch("paho.mqtt.client.Client")
    mqttwarn_context: Mock = mocker.patch("mqttwarn.core.context")

    # Run the `connect` function to completion.
    connect()

    assert mqtt_client.mock_calls == [
        call("testdrive", clean_session=False, protocol=3),
        call().username_pw_set("foo", None),
        call().connect("localhost", 1883, 60),
    ]
    assert mqttwarn_context.mock_calls == []


def test_connect_tls_success(mocker, caplog):
    """
    Verify the `connect()` function does the right thing when requesting MQTT broker authentication.
    """

    # Use a real configuration object.
    config = Config(defaults={"clientid": "testdrive"})
    config.tls = True
    mocker.patch("mqttwarn.core.cf", config)

    # Use mocked MQTT client and mqttwarn context instances.
    mqtt_client: Mock = mocker.patch("paho.mqtt.client.Client")
    mqttwarn_context: Mock = mocker.patch("mqttwarn.core.context")

    # Run the `connect` function to completion.
    connect()

    assert mqtt_client.mock_calls == [
        call("testdrive", clean_session=False, protocol=3),
        call().tls_set(None, None, None, tls_version=None, ciphers=None),
        call().connect("localhost", 1883, 60),
    ]
    assert mqttwarn_context.mock_calls == []


def test_connect_tls_insecure_success(mocker, caplog):
    """
    Verify the `connect()` function does the right thing when requesting MQTT broker authentication.
    """

    # Use a real configuration object.
    config = Config(defaults={"clientid": "testdrive"})
    config.tls_insecure = True
    mocker.patch("mqttwarn.core.cf", config)

    # Use mocked MQTT client and mqttwarn context instances.
    mqtt_client: Mock = mocker.patch("paho.mqtt.client.Client")
    mqttwarn_context: Mock = mocker.patch("mqttwarn.core.context")

    # Run the `connect` function to completion.
    connect()

    assert mqtt_client.mock_calls == [
        call("testdrive", clean_session=False, protocol=3),
        call().tls_insecure_set(True),
        call().connect("localhost", 1883, 60),
    ]
    assert mqttwarn_context.mock_calls == []


def test_connect_connection_failure(mocker, caplog):
    """
    Verify the `connect()` function fails when not able to establish connection to MQTT broker.
    """
    config = Config(defaults={"clientid": "testdrive"})
    mocker.patch("mqttwarn.core.cf", config)
    mocker.patch("paho.mqtt.client.Client.connect", side_effect=ValueError("Something failed"))
    with pytest.raises(SystemExit) as ex:
        connect()
    assert ex.value.code == 2
    assert ("mqttwarn.core", 10, "Attempting connection to MQTT broker localhost:1883") in caplog.record_tuples
    assert ("mqttwarn.core", 40, "Cannot connect to MQTT broker at localhost:1883") in caplog.record_tuples
    assert "ValueError: Something failed" in caplog.text


def test_connect_no_services_failure(mocker, caplog):
    """
    Verify the `connect()` function fails when there are no services configured.
    """
    mocker.patch("mqttwarn.core.cf")
    mocker.patch("mqttwarn.core.cf.getlist", side_effect=ValueError("Something failed"))
    with pytest.raises(SystemExit) as ex:
        connect()
    assert ex.value.code == 2
    assert ("mqttwarn.core", 40, "No services configured, aborting") in caplog.record_tuples


def test_on_connect_success(tmp_path, mocker, caplog):
    """
    Verify that the `on_connect` event handler works as intended on the happy path.
    """

    ini_file = tmp_path.joinpath("test-two-same-topics.ini")
    ini_file.touch()
    ini_file.write_text(
        """
    [defaults]

    [test/foo-1]
    topic   = test/foo
    targets = foo:void

    [test/foo-2]
    topic   = test/foo
    targets = foo:void
    """
    )

    config = Config(configuration_file=ini_file)
    context = RuntimeContext(config=config, invoker=None)

    mocker.patch("mqttwarn.core.cf", config)
    mocker.patch("mqttwarn.core.context", context)
    mqttc = mocker.patch("mqttwarn.core.mqttc")

    on_connect(mosq=None, userdata=None, flags=None, result_code=0)

    assert ("mqttwarn.core", 10, "Connected to MQTT broker, subscribing to topics") in caplog.record_tuples
    assert ("mqttwarn.core", 10, "Subscribing to test/foo (qos=0)") in caplog.record_tuples
    assert mqttc.mock_calls == [
        call.subscribe("test/foo", 0),
    ]


def test_on_connect_failures(caplog):
    """
    Verify that the `on_connect` event handler works as intended on different error paths.
    """
    result_codes = list(range(1, 6)) + [999]
    for result_code in result_codes:
        on_connect(mosq=None, userdata=None, flags=None, result_code=result_code)
    assert caplog.record_tuples == [
        ("mqttwarn.core", 40, "Connection refused - unacceptable protocol version"),
        ("mqttwarn.core", 40, "Connection refused - identifier rejected"),
        ("mqttwarn.core", 40, "Connection refused - server unavailable"),
        ("mqttwarn.core", 40, "Connection refused - bad user name or password"),
        ("mqttwarn.core", 40, "Connection refused - not authorised"),
        ("mqttwarn.core", 40, "Connection failed - result code 999"),
    ]


def test_on_disconnect_success(caplog):
    """
    Verify that the `on_disconnect` event handler works as intended on the happy path.
    """
    on_disconnect(mosq=None, userdata=None, result_code=0)
    assert caplog.record_tuples == [
        ("mqttwarn.core", 20, "Clean disconnection from broker"),
    ]


def test_on_disconnect_failure(mocker, caplog):
    """
    Verify that the `on_disconnect` event handler works as intended on the error path.
    """
    send_failover: Mock = mocker.patch("mqttwarn.core.send_failover")
    mocker.patch("mqttwarn.core.time.sleep")

    on_disconnect(mosq=None, userdata=None, result_code=999)
    assert caplog.record_tuples == []
    send_failover.assert_called_once_with(
        "brokerdisconnected", b"Broker connection lost. Will attempt to reconnect in 5s"
    )


def test_on_message_success():
    """
    Verify success path of `on_message`.
    """
    mosq = MqttClient()
    msg = MQTTMessage()
    on_message(mosq=mosq, userdata={}, msg=msg)


def test_on_message_failure(caplog, mocker):
    """
    Verify error path of `on_message`.
    """
    mosq = MqttClient()
    msg = MQTTMessage()
    mocker.patch("mqttwarn.core.on_message_handler", side_effect=Exception)
    on_message(mosq=mosq, userdata={}, msg=msg)
    assert "Receiving and decoding MQTT message failed" in caplog.messages


def test_send_failover_no_targets(mocker, caplog):
    """
    Verify the `send_failover` function.
    """
    mocker.patch("mqttwarn.core.cf", has_section=lambda _: False)
    send_failover("foobar", "Something failed")
    assert caplog.record_tuples == [
        ("mqttwarn.core", 30, "Something failed"),
        ("mqttwarn.core", 30, "Section [failover] does not exist in your INI file, skipping message on topic 'foobar'"),
    ]


def test_subscribe_forever_success(caplog, mocker):
    """
    Verify the `core.subscribe_forever` function.
    """

    # FIXME: Make it work on Windows.
    if sys.platform.startswith("win"):
        raise pytest.xfail("Skipping test, fails on Windows")

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
    connect.return_value = Mock(**{"loop_forever.side_effect": socket.error("Something failed")})
    t = threading.Thread(target=subscribe_forever)
    t.start()
    mocker.patch("mqttwarn.core.exit_flag", True)
    t.join()

    assert connect.mock_calls == [call(), call().loop_forever()]

    assert (
        "mqttwarn.core",
        40,
        "Connection to MQTT broker lost: OSError(Something failed)",
    ) in caplog.record_tuples or (
        "mqttwarn.core",
        30,
        "MQTT server disconnected, trying to reconnect each 5 seconds",
    ) in caplog.record_tuples


def test_subscribe_forever_fails_unknown_error(caplog, mocker):
    """
    Verify the `core.subscribe_forever` function correctly reports about errors.
    """

    # Adjust plumbing to speed up test case.
    mocker.patch("time.sleep", lambda _: delay(0.05))

    # Invoke `subscribe_forever` and terminate right away using `exit_flag`.
    connect = mocker.patch("mqttwarn.core.connect")
    connect.return_value = Mock(**{"loop_forever.side_effect": ValueError("Something failed")})

    # Invoke `subscribe_forever` in a different thread, but get hold of its exception through a `Future`.
    with ThreadPoolExecutor() as executor:
        future = executor.submit(subscribe_forever)
        mocker.patch("mqttwarn.core.exit_flag", True)
        with pytest.raises(ValueError) as ex:
            future.result(timeout=1)
        assert ex.match("Something failed")

    assert connect.mock_calls == [call(), call().loop_forever()]

    assert caplog.record_tuples == [
        ("mqttwarn.core", 40, "Connection to MQTT broker lost: ValueError(Something failed)"),
    ]


def test_functions_bad(tmp_ini, caplog):
    """
    Verify the behavior when loading an invalid `functions` file.
    `tests/etc/functions_bad.py` features an `IndentationError`.
    """

    tmp_ini.write_text(
        """
[defaults]
functions = 'tests/etc/functions_bad.py'
    """
    )

    with pytest.raises(IndentationError) as ex:
        core_bootstrap(configfile=tmp_ini)
    assert ex.match("unexpected indent")


def test_cron_success(tmp_ini, mocker, caplog):
    """
    Approve the `cron` subsystem on the happy path.
    """

    tmp_ini.write_text(
        """
[defaults]
functions = 'tests/etc/functions_good.py'

[cron]
cronfunc = 0.5; now=true
    """
    )

    mocker.patch("sys.exit")
    mqttc = mocker.patch("mqttwarn.core.mqttc")

    # Bootstrap the core machinery without MQTT, and shut it down again.
    core_bootstrap(configfile=tmp_ini)
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


def test_cron_without_functions_failure(tmp_ini, caplog):
    """
    Verify that mqttwarn croaks when configuring a `cron` function, but no `function` file.
    """

    tmp_ini.write_text(
        """
[defaults]

[cron]
cronfunc = 0.5; now=true
    """
    )

    with pytest.raises(AssertionError) as ex:
        core_bootstrap(configfile=tmp_ini)
    assert ex.match("Python module must be given")


def test_cron_function_missing_failure(tmp_ini, caplog):
    """
    Verify that mqttwarn warns when configuring a non-existent `cron` function.
    """

    tmp_ini.write_text(
        """
[defaults]
functions = 'tests/etc/functions_good.py'

[cron]
unknown = 0.5; now=true
    """
    )

    core_bootstrap(configfile=tmp_ini)

    assert (
        "mqttwarn.core",
        40,
        "[cron] section has function [unknown] specified, but that's not defined",
    ) in caplog.record_tuples


def test_invalid_config(tmp_ini, caplog):
    """
    Verify that mqttwarn croaks when using an invalid configuration file.
    """

    tmp_ini.write_text(
        """
# The error within this configuration file is that the closing brace `}` of the
# `targets` dictionary is not indented. This is an artifact of `ConfigParser`.
[foo/bar]
targets = {
  'test/targets-dict/info': 'log:info',
  'test/targets-dict/warn': 'log:warn',
}
    """
    )

    with pytest.raises(configparser.ParsingError) as ex:
        core_bootstrap(configfile=tmp_ini)
    assert ex.match("Source contains parsing errors")


def test_xform():
    """
    Evaluates certain behaviors of `test_xform`.
    """
    assert xform(None, None, None) is None


def test_publish_status_information_success(mocker, caplog):
    """
    Verify calling the `publish_status_information` function works as expected.
    """

    # Use a real configuration object.
    config = Config()
    config.add_section("defaults")
    config.set("defaults", "status_publish", True)
    config.status_publish = True
    mocker.patch("mqttwarn.core.cf", config)

    # Mock the MQTT client instance.
    mqtt_client: Mock = mocker.patch("mqttwarn.core.mqttc")

    publish_status_information()

    assert mqtt_client.mock_calls == [
        call.publish("mqttwarn/$SYS/version", mock.ANY, retain=True),
        call.publish("mqttwarn/$SYS/platform", mock.ANY, retain=True),
        call.publish("mqttwarn/$SYS/python/version", mock.ANY, retain=True),
    ]

    assert caplog.record_tuples == [
        ("mqttwarn.core", 20, "Publishing status information to mqttwarn/$SYS"),
    ]


def test_publish_status_information_failure(mocker, caplog):
    """
    Verify calling the `publish_status_information` croaks as expected, when publishing fails.
    """

    # Use a real configuration object.
    config = Config()
    config.add_section("defaults")
    config.set("defaults", "status_publish", True)
    config.status_publish = True
    mocker.patch("mqttwarn.core.cf", config)

    # Mock the MQTT client instance.
    mqtt_client: Mock = mocker.patch("mqttwarn.core.mqttc")
    mocker.patch("mqttwarn.core.mqttc.publish", side_effect=ValueError("Something failed"))

    publish_status_information()

    assert mqtt_client.mock_calls == []

    assert caplog.record_tuples == [
        ("mqttwarn.core", 20, "Publishing status information to mqttwarn/$SYS"),
        ("mqttwarn.core", 40, "Unable to publish status information"),
    ]


def test_processor(tmp_ini, caplog):
    """
    Verify job dispatching w/o any target address information works (2021-10-18 [amo]).
    """
    import mqttwarn.core

    mqttwarn.core.exit_flag = True
    mqttwarn.core.processor()
    assert "Worker thread exiting" in caplog.messages


def test_load_services_success():
    """
    Verify loading a service without further ado succeeds.
    """
    config = Config()
    config.add_section("config:noop")
    bootstrap(config=config)
    load_services(["noop"])


def test_load_services_unknown():
    """
    Loading an unknown service should fail.
    """
    config = Config()
    bootstrap(config=config)
    with pytest.raises(KeyError) as ex:
        load_services(["unknown"])
    assert ex.match("Configuration section does not exist: config:unknown")


def test_load_services_spec_not_found(caplog):
    """
    Loading a service where its module can not be discovered from a module specification, should fail.
    """
    config = Config()
    config.add_section("config:foo.bar")
    bootstrap(config=config)
    with pytest.raises(ImportError) as ex:
        load_services(["foo.bar"])
    assert 'Loading service "foo.bar" from module "foo.bar" failed' in caplog.messages
    assert "Failed loading service: foo.bar" in caplog.messages
    assert ex.match("Failed loading service: foo.bar")


def test_load_services_file_not_found(tmp_path, caplog):
    """
    Loading a service where its module can not be discovered from a file name path, should fail.
    """

    modulefile = tmp_path / "foo_bar.py"

    config = Config()
    config.configuration_path = tmp_path
    config.add_section("config:foo.bar")
    config.set("config:foo.bar", "module", "foo_bar.py")
    bootstrap(config=config)
    with pytest.raises(ImportError) as ex:
        load_services(["foo.bar"])
    assert 'Module "foo_bar.py" is not a file' in caplog.messages
    assert f'Module "{modulefile}" is not a file' in caplog.messages
    assert "Failed loading service: foo.bar" in caplog.messages
    assert ex.match("Failed loading service: foo.bar")


def test_load_services_file_failure(tmp_path, caplog):
    """
    When loading a module fails at runtime, mqttwarn should fail.
    """

    # Prepare a Python module which will raise an exception when loaded.
    modulefile = tmp_path / "foo_bar.py"
    modulefile.write_text("assert 1 == 2\n")

    config = Config()
    config.configuration_path = tmp_path
    config.add_section("config:foo.bar")
    config.set("config:foo.bar", "module", "foo_bar.py")
    bootstrap(config=config)

    with pytest.raises(ImportError) as ex:
        load_services(["foo.bar"])
    assert f'Loading service "foo.bar" from file "{modulefile}" failed' in caplog.text
    assert "AssertionError" in caplog.text
    assert "Failed loading service: foo.bar" in caplog.messages
    assert ex.match("Failed loading service: foo.bar")


def test_run_plugin_success(caplog):
    """
    Verify running a plugin standalone works well.
    """
    config = Config()
    config.add_section("config:noop")
    run_plugin(config=config, name="noop")
    assert 'Successfully loaded service "noop"' in caplog.messages
    assert "Successfully sent message using noop" in caplog.messages
    assert "Plugin response: True" in caplog.messages


def test_run_plugin_failure(caplog):
    """
    Verify running a plugin standalone works well, and runtime failures will be signalled properly.
    """
    config = Config()
    config.add_section("config:noop")
    with pytest.raises(SystemExit) as ex:
        run_plugin(config=config, name="noop", message="fail")
    assert ex.match("1")

    assert 'Successfully loaded service "noop"' in caplog.messages
    assert "Failed sending message using noop" in caplog.messages
    assert "Plugin response: False" in caplog.messages


def test_run_plugin_module_success(caplog):
    """
    Verify running a plugin standalone works well, when addressing it as a full-qualified module name.
    """
    config = Config()
    config.add_section("config:mqttwarn.services.noop")
    run_plugin(config=config, name="mqttwarn.services.noop")
    assert (
        'Successfully loaded service "mqttwarn.services.noop" from module "mqttwarn.services.noop"' in caplog.messages
    )
    assert "Successfully sent message using noop" in caplog.messages
    assert "Plugin response: True" in caplog.messages
