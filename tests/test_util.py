# -*- coding: utf-8 -*-
# (c) 2018-2023 The mqttwarn developers
from __future__ import division

import py_compile
import re
import time
import types
from builtins import str

import pytest

from mqttwarn.util import (
    Formatter,
    asbool,
    get_resource_content,
    import_symbol,
    load_file,
    load_function,
    load_functions,
    load_module_by_name,
    load_module_from_file,
    parse_cron_options,
    sanitize_function_name,
    timeout,
)
from tests import configfile_full, funcfile_bad, funcfile_good


def test_formatter_basic():
    result = Formatter().format("{foo}", **{"foo": "Räuber Hotzenplotz"}).encode("utf-8")
    assert result == b"R\xc3\xa4uber Hotzenplotz"


def test_formatter_json():
    result = Formatter().format("{foo!j}", **{"foo": {"bar": "Räuber Hotzenplotz"}}).encode("utf-8")
    assert result == b'{"bar": "R\\u00e4uber Hotzenplotz"}'


def test_asbool():
    assert asbool(True) is True
    assert asbool(False) is False
    assert asbool(None) is False
    assert asbool("true") is True
    assert asbool("false") is False
    assert asbool("yes") is True
    assert asbool("no") is False
    assert asbool("on") is True
    assert asbool("off") is False

    with pytest.raises(ValueError) as excinfo:
        asbool("Hotzenplotz")
    assert str(excinfo.value) == "String is not true/false: 'hotzenplotz'"


def test_parse_cron_options():
    assert parse_cron_options("60; now=true") == {"now": "true", "interval": 60.0}


def test_timeout():
    def func():
        time.sleep(0.3)
        return 42

    def errfunc():
        raise ValueError("Something went wrong")

    assert timeout(func, timeout_secs=0.1) is False
    assert timeout(func, timeout_secs=0.5) == 42

    # FIXME: Better catch and report the exception?
    # FIXME: Derive "timeout_secs" from "duration"
    with pytest.raises(ValueError) as excinfo:
        timeout(errfunc, timeout_secs=0.1, default="foobar")

    assert str(excinfo.value) == "Something went wrong"


def test_sanitize_function_name():
    assert sanitize_function_name("foobar()") == "foobar"

    with pytest.raises(ValueError) as ex:
        sanitize_function_name("hastme")
    assert ex.match("Invalid function name: hastme")

    with pytest.raises(ValueError) as ex:
        sanitize_function_name(42)
    assert ex.match("Invalid function name: 42")

    with pytest.raises(ValueError) as ex:
        sanitize_function_name(None)
    assert ex.match("Empty function name: None")


def test_load_module_from_file_good():
    module = load_module_from_file("mqttwarn/services/file.py")
    assert "plugin" in dir(module)
    assert module.plugin.__code__.co_argcount == 2
    assert "srv" in module.plugin.__code__.co_varnames
    assert "item" in module.plugin.__code__.co_varnames


def test_load_module_from_file_bad():
    with pytest.raises(IOError) as excinfo:
        load_module_from_file("mqttwarn/services/unknown.py")
        assert str(excinfo.value) == "IOError: [Errno 2] No such file or directory: 'mqttwarn/services/unknown.py'"


def test_load_module_by_name_good():
    module = load_module_by_name("mqttwarn.services.file")
    assert "plugin" in dir(module)
    assert module.plugin.__code__.co_argcount == 2
    assert "srv" in module.plugin.__code__.co_varnames
    assert "item" in module.plugin.__code__.co_varnames


def test_load_module_by_name_bad():
    with pytest.raises(ImportError) as excinfo:
        load_module_by_name("mqttwarn.services.unknown")
        assert str(excinfo.value) == "ImportError: No module named unknown"


def test_load_functions():

    # Load valid functions file
    py_mod = load_functions(filepath=funcfile_good)
    assert py_mod is not None

    # No-op
    py_mod = load_functions(filepath=None)
    assert py_mod is None

    # Load missing functions file
    with pytest.raises(IOError) as excinfo:
        load_functions(filepath="unknown.txt")
    assert str(excinfo.value) == "'{}' not found".format("unknown.txt")

    # Load functions file that is not a python file
    with pytest.raises(ImportError) as excinfo:
        load_functions(filepath=configfile_full)
    assert re.match(r"Loading file failed \(only .py and .pyc\): .+full.ini", str(excinfo.value))

    # Load bad functions file
    with pytest.raises(Exception):
        load_functions(filepath=funcfile_bad)


def test_load_functions_pyc(tmp_path):
    """
    Verify loading valid byte-compiled functions file (.pyc) succeeds.

    https://docs.python.org/3/library/py_compile.html
    """

    funcfile_pyc = str(tmp_path.joinpath("funcfile.pyc"))
    py_compile.compile(file=funcfile_good, cfile=funcfile_pyc)

    py_mod = load_functions(filepath=funcfile_pyc)
    assert py_mod is not None


def test_load_function():

    # Load valid functions file
    py_mod = load_functions(filepath=funcfile_good)
    assert py_mod is not None

    # Load valid function
    func = load_function(name="foobar", py_mod=py_mod)
    assert func is not None

    # Load invalid function, function name does not exist in "funcfile_good"
    with pytest.raises(AttributeError) as excinfo:
        load_function(name="unknown", py_mod=py_mod)
    assert re.match(
        "Function 'unknown' does not exist in '.+functions_good.py'",
        str(excinfo.value),
    )


def test_get_resource_content():
    payload = get_resource_content("mqttwarn.examples", "basic/mqttwarn.ini")
    assert "[defaults]" in payload


def test_import_symbol_module_success():
    """
    Proof that the `import_symbol` function works as intended.
    """
    symbol = import_symbol("mqttwarn.services.log")
    assert symbol.__name__ == "mqttwarn.services.log"
    assert isinstance(symbol, types.ModuleType)


def test_import_symbol_module_fail():
    """
    Proof that the `import_symbol` function works as intended.
    """
    with pytest.raises(ImportError) as ex:
        import_symbol("foo.bar.baz")
    assert ex.match("Symbol not found: foo.bar.baz")


def test_import_symbol_function_success():
    """
    Proof that the `import_symbol` function works as intended.
    """
    symbol = import_symbol("mqttwarn.services.log.plugin")
    assert symbol.__name__ == "plugin"
    assert isinstance(symbol, types.FunctionType)


def test_import_symbol_function_fail():
    """
    Proof that the `import_symbol` function works as intended.
    """
    with pytest.raises(ImportError) as ex:
        import_symbol("mqttwarn.services.log.foo.bar.baz")
    assert ex.match("Symbol not found: foo.bar.baz, module=<module 'mqttwarn.services.log' from")


def test_load_file_success(tmp_path):
    tmpfile = tmp_path / "foo.txt"
    tmpfile.write_text("Hello, world.")
    payload = load_file(tmpfile)
    assert payload.read() == b"Hello, world."


def test_load_file_failure(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_file("/tmp/foobar.txt", retry_tries=0)
