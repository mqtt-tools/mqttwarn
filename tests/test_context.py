# -*- coding: utf-8 -*-
# (c) 2022 The mqttwarn developers
import pytest
from mqttwarn.configuration import Config
from mqttwarn.context import FunctionInvoker, RuntimeContext


@pytest.fixture
def runtime_ini_file(tmp_path):
    """
    Provide an INI file to the `RuntimeContext` test cases.
    """
    ini_file = tmp_path.joinpath("test-runtime-context.ini")
    ini_file.touch()
    ini_file.write_text(
        """
    [defaults]

    [cron]
    cronfunc = 0.5; now=true

    [failover]
    targets  = foo:void, bar
    title    = mqttwarn

    [config:foo]
    targets = {"abc": "def"}
    qos     = 1
    filter  = filter_function()
    datamap = datamap_function()
    alldata = alldata_function()

    [test/topic]
    topic   = test/foo
    targets = foo:void
    format  = Something {message}

    [test/topic-without-targets]
    format  = Something {message}
    """
    )
    return ini_file


def test_runtime_context_get_sections(caplog, runtime_ini_file):
    """
    Verify the `RuntimeContext.get_sections` method.
    """

    config = Config(configuration_file=runtime_ini_file)
    context = RuntimeContext(config=config, invoker=None)
    assert context.get_sections() == ["test/topic"]
    assert caplog.messages == ["Section `test/topic-without-targets' has no targets defined"]


def test_runtime_context_get_more(caplog, runtime_ini_file):
    """
    Verify the `RuntimeContext.{get_topic,get_qos,get_config}` methods.
    """

    config = Config(configuration_file=runtime_ini_file)
    context = RuntimeContext(config=config, invoker=None)
    assert context.get_topic("test/topic") == "test/foo"
    assert context.get_topic("test/topic-without-targets") == "test/topic-without-targets"
    assert context.get_qos("config:foo") == 1
    assert context.get_config("failover", "title") == "mqttwarn"
    assert caplog.messages == []


def test_runtime_context_callfunc_failures(caplog, runtime_ini_file):
    """
    Verify the `RuntimeContext.{is_filtered,get_topic_data,get_all_data}` methods.
    """

    config = Config(configuration_file=runtime_ini_file)

    invoker = FunctionInvoker(config=config, srv=None)
    context = RuntimeContext(config=config, invoker=invoker)
    assert context.is_filtered(section="config:foo", topic="foo", payload="bar") is False
    assert context.get_topic_data(section="config:foo", topic="foo") is None
    assert context.get_all_data(section="config:foo", topic="foo", data="bar") is None
    assert caplog.messages == [
        "Cannot invoke filter function 'filter_function' defined in 'config:foo': Python module must be given",
        "Cannot invoke datamap function 'datamap_function' defined in 'config:foo': Python module must be given",
        "Cannot invoke alldata function 'alldata_function' defined in 'config:foo': Python module must be given",
    ]


def test_runtime_context_get_service_config(runtime_ini_file):
    """
    Verify the `RuntimeContext.get_service_config` method.
    """
    config = Config(configuration_file=runtime_ini_file)
    context = RuntimeContext(config=config, invoker=None)
    assert context.get_service_config("foo") == {
        "alldata": "alldata_function()",
        "datamap": "datamap_function()",
        "filter": "filter_function()",
        "qos": 1,
    }
    assert context.get_service_config("unknown") == {}


def test_runtime_context_get_service_targets(runtime_ini_file):
    """
    Verify the `RuntimeContext.get_service_targets` method.
    """
    config = Config(configuration_file=runtime_ini_file)
    context = RuntimeContext(config=config, invoker=None)
    assert context.get_service_targets("foo") == {"abc": "def"}
    assert context.get_service_targets("unknown") is None
