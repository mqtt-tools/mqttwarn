# -*- coding: utf-8 -*-
# (c) 2018-2019 The mqttwarn developers
from __future__ import division
import re
from builtins import str
from past.utils import old_div
import time
import pytest
from mqttwarn.util import Struct, Formatter, asbool, parse_cron_options, timeout, sanitize_function_name, load_module, \
    load_functions, load_function, get_resource_content, exception_traceback
from tests import funcfile, configfile, bad_funcfile


def test_struct():
    data = {'hello': 'world'}
    struct = Struct(**data)
    assert struct.hello == 'world'
    assert struct.get('hello') == 'world'
    assert struct.get('unknown', default=42) == 42
    assert repr(struct) == "<hello: 'world'>"
    assert struct.enum() == data


def test_formatter_basic():
    result = Formatter().format("{foo}", **{u'foo': u'Räuber Hotzenplotz'}).encode('utf-8')
    assert result == b'R\xc3\xa4uber Hotzenplotz'


def test_formatter_json():
    result = Formatter().format("{foo!j}", **{u'foo': {u'bar': u'Räuber Hotzenplotz'}}).encode('utf-8')
    assert result == b'{"bar": "R\\u00e4uber Hotzenplotz"}'


def test_asbool():
    assert asbool(True) is True
    assert asbool(False) is False
    assert asbool(None) is False
    assert asbool('true') is True
    assert asbool('false') is False
    assert asbool('yes') is True
    assert asbool('no') is False
    assert asbool('on') is True
    assert asbool('off') is False

    with pytest.raises(ValueError) as excinfo:
        asbool('Hotzenplotz')
    assert str(excinfo.value) == "String is not true/false: 'hotzenplotz'"


def test_parse_cron_options():
    assert parse_cron_options('60; now=true') == {'now': 'true', 'interval': 60.0}


#@pytest.mark.slow
def test_timeout():

    duration = 0.0005
    below_duration = duration - old_div(duration, 2)
    above_duration = duration + old_div(duration, 2)

    def func():
        time.sleep(duration)
        return 42

    def errfunc():
        raise ValueError('Something went wrong')

    assert timeout(func, timeout_secs=below_duration) is False
    assert timeout(func, timeout_secs=above_duration) == 42

    # FIXME: Better catch and report the exception?
    # FIXME: Derive "timeout_secs" from "duration"
    with pytest.raises(ValueError) as excinfo:
        timeout(errfunc, timeout_secs=0.10, default='foobar')
        excinfo.message == 'Something went wrong'


def test_sanitize_function_name():
    assert sanitize_function_name('foobar()') == 'foobar'
    assert sanitize_function_name('hastme') is None
    assert sanitize_function_name(42) is None
    assert sanitize_function_name(None) is None


def test_load_module():
    module = load_module('mqttwarn/services/file.py')
    assert 'plugin' in dir(module)
    assert module.plugin.__code__.co_argcount == 2
    assert 'srv' in module.plugin.__code__.co_varnames
    assert 'item' in module.plugin.__code__.co_varnames


def test_load_functions():

    # Load valid functions file
    py_mod = load_functions(filepath=funcfile)
    assert py_mod is not None

    # No-op
    py_mod = load_functions(filepath=None)
    assert py_mod is None

    # Load missing functions file
    with pytest.raises(IOError) as excinfo:
        load_functions(filepath='unknown.txt')
    assert str(excinfo.value) == "'{}' not found".format('unknown.txt')

    # Load functions file that is not a python file
    with pytest.raises(ValueError) as excinfo:
        load_functions(filepath=configfile)
    assert str(excinfo.value) == "'{}' does not have the .py or .pyc extension".format(configfile)

    # Load bad functions file
    with pytest.raises(Exception):
        load_functions(filepath=bad_funcfile)


def test_load_function():

    # Load valid functions file
    py_mod = load_functions(filepath=funcfile)
    assert py_mod is not None

    # Load valid function
    func = load_function(name='foobar', py_mod=py_mod)
    assert func is not None

    # Load invalid function, function name does not exist in "funcfile"
    with pytest.raises(AttributeError) as excinfo:
        load_function(name='unknown', py_mod=py_mod)
    assert re.match("Function 'unknown' does not exist in '{}c?'".format(funcfile), str(excinfo.value))


def test_get_resource_content():
    payload = get_resource_content('mqttwarn.examples', 'basic/mqttwarn.ini')
    assert '[defaults]' in payload


def test_exception_traceback():

    # Get exception from ``sys.exc_info()``
    try:
        raise ValueError('Something reasonable')

    except Exception as ex:
        tb = exception_traceback()
        assert 'ValueError: Something reasonable' in tb
