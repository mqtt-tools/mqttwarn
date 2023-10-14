# (c) 2014-2023 The mqttwarn developers
import functools
import importlib.machinery

try:
    from importlib.resources import files as resource_files  # type: ignore[attr-defined]
except ImportError:
    from importlib_resources import files as resource_files  # type: ignore[no-redef]

import importlib.util
import json
import logging
import os
import re
import string
import types
import typing as t
from pathlib import Path

import funcy
from six import string_types

if t.TYPE_CHECKING:
    from importlib._bootstrap_external import FileLoader

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

        See also https://github.com/mqtt-tools/mqttwarn/issues/146.
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


def load_module_from_file(path: t.Union[str, Path]) -> types.ModuleType:
    """
    http://code.davidjanes.com/blog/2008/11/27/how-to-dynamically-load-python-code/

    :param path:
    :return:
    """
    path = Path(path)
    name = path.stem
    loader: "FileLoader"
    if path.suffix == ".py":
        loader = importlib.machinery.SourceFileLoader(fullname=name, path=str(path))
    elif path.suffix == ".pyc":
        loader = importlib.machinery.SourcelessFileLoader(fullname=name, path=str(path))
    else:
        raise ImportError(f"Loading file failed (only .py and .pyc): {path}")
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise ModuleNotFoundError(f"Failed loading module from file: {path}")
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def load_module_by_name(name: str) -> types.ModuleType:
    """
    https://pymotw.com/2/imp/#loading-modules

    :param name:
    :return:
    """
    module = import_symbol(name)
    return module


def import_symbol(name: str, parent: t.Optional[types.ModuleType] = None) -> types.ModuleType:
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

    parent_name = None
    next_module_real = next_module

    if parent is not None:
        next_module_real = "." + next_module
        parent_name = parent.__name__
    try:
        spec = importlib.util.find_spec(next_module_real, parent_name)
    except (AttributeError, ModuleNotFoundError):
        module = parent
        if module is None or module.__loader__ is None:
            raise ImportError(f"Symbol not found: {name}")
        if hasattr(module, next_module):
            return getattr(module, next_module)
        else:
            raise ImportError(f"Symbol not found: {name}, module={module}")

    if spec is None:
        msg = f"Symbol not found: {name}"
        if parent is not None:
            msg += f", module={parent.__name__}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)

    # Actually load the module.
    loader: FileLoader = module.__loader__
    loader.exec_module(module)

    if remaining_names is None:
        return module

    return import_symbol(remaining_names, parent=module)


def load_functions(filepath: t.Optional[str] = None) -> t.Optional[types.ModuleType]:

    if not filepath:
        return None

    if not os.path.isfile(filepath):
        raise IOError("'{}' not found".format(filepath))

    py_mod = load_module_from_file(filepath)
    return py_mod


def load_function(name: str, py_mod: t.Optional[types.ModuleType]) -> t.Callable:
    assert name, "Function name must be given"
    assert py_mod, "Python module must be given"

    func = getattr(py_mod, name, None)

    if func is None:
        raise AttributeError("Function '{}' does not exist in '{}'".format(name, py_mod.__file__))

    return func


def get_resource_content(package: str, filename: str) -> str:
    path = resource_files(package) / filename
    return path.read_text()


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
