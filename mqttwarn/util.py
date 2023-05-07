# (c) 2014-2023 The mqttwarn developers
import functools
import hashlib
import imp
import json
import logging
import os
import re
import string
import types
import typing as t
from pathlib import Path

import funcy
import pkg_resources
from six import string_types

logger = logging.getLogger(__name__)


class Formatter(string.Formatter):
    """
    A custom string formatter. See also:
    - https://docs.python.org/2/library/string.html#format-string-syntax
    - https://docs.python.org/2/library/string.html#custom-string-formatting
    """

    def convert_field(self, value: str, conversion: str) -> str:
        """
        The conversion field causes a type coercion before formatting.
        By default, two conversion flags are supported: '!s' which calls
        str() on the value, and '!r' which calls repr().

        This also adds the '!j' conversion flag, which serializes the
        value to JSON format.

        See also https://github.com/jpmens/mqttwarn/issues/146.
        """
        if conversion == "j":
            value = json.dumps(value)
        return value


def asbool(obj: t.Any) -> bool:
    """
    Shamelessly stolen from beaker.converters
    # (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
    # Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
    """
    if isinstance(obj, string_types):
        obj = obj.strip().lower()
        if obj in ["true", "yes", "on", "y", "t", "1"]:
            return True
        elif obj in ["false", "no", "off", "n", "f", "0"]:
            return False
        else:
            raise ValueError("String is not true/false: %r" % obj)
    return bool(obj)


def parse_cron_options(argstring: str) -> t.Dict[str, t.Union[str, float]]:
    """
    Parse periodic task options.
    Obtains configuration value, returns dictionary.

    Example::

        my_periodic_task = 60; now=true

    Respective "argstring"::

        60; now=true

    """
    parts = argstring.split(";")
    options: t.Dict[str, t.Union[str, float]] = {"interval": float(parts[0].strip())}
    for part in parts[1:]:
        name, value = part.split("=")
        options[name.strip()] = value.strip()
    return options


# http://code.activestate.com/recipes/473878-timeout-function-using-threading/
def timeout(func: t.Callable, args=(), kwargs={}, timeout_secs: int = 10, default: bool = False) -> t.Any:
    import threading

    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None
            self.exception = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)

            # FIXME: Shouldn't we report this better?
            except Exception as ex:
                self.result = default
                self.exception = ex

    it = InterruptableThread()
    it.start()
    it.join(timeout_secs)

    if it.exception is not None:
        raise it.exception

    if it.is_alive():
        return default
    else:
        return it.result


def sanitize_function_name(name: str) -> str:
    if name is None:
        raise ValueError(f"Empty function name: {name}")

    try:
        valid = re.match(r"^[\w]+\(\)", name)
        if valid is not None:
            return re.sub("[()]", "", name)
    except:
        pass
    raise ValueError(f"Invalid function name: {name}")


def load_module_from_file(path: str) -> types.ModuleType:
    """
    http://code.davidjanes.com/blog/2008/11/27/how-to-dynamically-load-python-code/

    :param path:
    :return:
    """
    try:
        fp = open(path, "rb")
        digest = hashlib.md5(path.encode("utf-8")).hexdigest()
        return imp.load_source(digest, path, fp)  # type: ignore[arg-type]
    finally:
        try:
            fp.close()
        except:
            pass


def load_module_by_name(name: str) -> types.ModuleType:
    """
    https://pymotw.com/2/imp/#loading-modules

    :param name:
    :return:
    """
    module = import_module(name)
    return module


def import_module(name: str, path: t.Optional[t.List[str]] = None) -> types.ModuleType:
    """
    Derived from `import_from_dotted_path`:
    https://chase-seibert.github.io/blog/2014/04/23/python-imp-examples.html

    import_from_dotted_path('foo.bar') -> from foo import bar; return bar
    """

    try:
        next_module, remaining_names = name.split(".", 1)
    except ValueError:
        next_module = name
        remaining_names = None

    fp, pathname, description = imp.find_module(next_module, path)
    module = imp.load_module(next_module, fp, pathname, description)  # type: ignore[arg-type]

    if remaining_names is None:
        return module

    if hasattr(module, remaining_names):
        return getattr(module, remaining_names)
    else:
        return import_module(remaining_names, path=list(module.__path__))


def load_functions(filepath: t.Optional[str] = None) -> t.Optional[types.ModuleType]:

    if not filepath:
        return None

    if not os.path.isfile(filepath):
        raise IOError("'{}' not found".format(filepath))

    mod_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == ".py":
        py_mod = imp.load_source(mod_name, filepath)

    elif file_ext.lower() == ".pyc":
        py_mod = imp.load_compiled(mod_name, filepath)

    else:
        raise ValueError("'{}' does not have the .py or .pyc extension".format(filepath))

    return py_mod


def load_function(name: str, py_mod: t.Optional[types.ModuleType]) -> t.Callable:
    assert name, "Function name must be given"
    assert py_mod, "Python module must be given"

    func = getattr(py_mod, name, None)

    if func is None:
        raise AttributeError("Function '{}' does not exist in '{}'".format(name, py_mod.__file__))

    return func


def get_resource_content(package: str, filename: str) -> str:
    with pkg_resources.resource_stream(package, filename) as stream:
        return stream.read().decode("utf-8")


def truncate(s: t.Union[str, bytes], limit: int = 200, ellipsis="...") -> str:
    try:
        if isinstance(s, bytes):
            s = s.decode("utf-8")
    except UnicodeDecodeError:
        pass
    s = str(s)
    s = s.strip()
    if len(s) > limit:
        return s[:limit].strip() + ellipsis
    return s


def load_file(path: t.Union[str, Path], retry_tries=None, retry_interval=0.075, unlink=False) -> t.IO[bytes]:
    """
    Load file content from filesystem gracefully, with optional retrying.

    TODO: Use better variant.
          https://github.com/Suor/funcy/issues/126#issuecomment-1527279230
    """
    call = functools.partial(open, path, "rb")
    if retry_tries:
        logger.info(f"Retry loading file {path} for {retry_tries} times")
        reader = funcy.retry(tries=int(retry_tries), timeout=float(retry_interval))(call)()
    else:
        reader = call()
    if unlink:
        try:
            os.unlink(path)
        except:  # pragma: nocover
            pass
    return reader
