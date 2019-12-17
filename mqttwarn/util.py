# -*- coding: utf-8 -*-
# (c) 2014-2019 The mqttwarn developers
from builtins import str
import os
import re
import imp
import sys
import json
import string
import traceback
import pkg_resources
from six import StringIO, string_types

try:
    import hashlib
    md = hashlib.md5
except ImportError:
    import md5
    md = md5.new


class Struct:
    """
    Convert Python dict to object?
    http://stackoverflow.com/questions/1305532/
    """
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        return '<%s>' % str("\n ".join("%s: %s" % (k, repr(v)) for (k, v) in list(self.__dict__.items())))

    def get(self, key, default=None):
        if key in self.__dict__ and self.__dict__[key] is not None:
            return self.__dict__[key]
        else:
            return default

    def enum(self):
        item = {}
        for (k, v) in list(self.__dict__.items()):
            item[k] = v
        return item


class Formatter(string.Formatter):
    """
    A custom string formatter. See also:
    - https://docs.python.org/2/library/string.html#format-string-syntax
    - https://docs.python.org/2/library/string.html#custom-string-formatting
    """

    def convert_field(self, value, conversion):
        """
        The conversion field causes a type coercion before formatting.
        By default, two conversion flags are supported: '!s' which calls
        str() on the value, and '!r' which calls repr().

        This also adds the '!j' conversion flag, which serializes the
        value to JSON format.

        See also https://github.com/jpmens/mqttwarn/issues/146.
        """
        if conversion == 'j':
            value = json.dumps(value)
        return value


def asbool(obj):
    """
    Shamelessly stolen from beaker.converters
    # (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
    # Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
    """
    if isinstance(obj, string_types):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)


def parse_cron_options(argstring):
    """
    Parse periodic task options.
    Obtains configuration value, returns dictionary.

    Example::

        my_periodic_task = 60; now=true

    Respective "argstring"::

        60; now=true

    """
    parts = argstring.split(';')
    options = {'interval': float(parts[0].strip())}
    for part in parts[1:]:
        name, value = part.split('=')
        options[name.strip()] = value.strip()
    return options


# http://code.activestate.com/recipes/473878-timeout-function-using-threading/
def timeout(func, args=(), kwargs={}, timeout_secs=10, default=False):
    import threading

    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)

            # FIXME: Shouldn't we report this better?
            except:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_secs)
    if it.is_alive():
        return default
    else:
        return it.result


def sanitize_function_name(s):
    func = None

    if s is not None:
        try:
            valid = re.match('^[\w]+\(\)', s)
            if valid is not None:
                func = re.sub('[()]', '', s)
        except:
            pass
    return func


# http://code.davidjanes.com/blog/2008/11/27/how-to-dynamically-load-python-code/
def load_module(path):
    try:
        fp = open(path, 'rb')
        digest = md(path.encode('utf-8')).hexdigest()
        return imp.load_source(digest, path, fp)
    finally:
        try:
            fp.close()
        except:
            pass


def load_function(name=None, filepath=None):
    mod_inst = None

    assert name, 'Function name must be given'
    assert filepath, 'Path to file must be given'

    mod_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, filepath)

    else:
        raise RuntimeError("Loading Python code from '{}' failed".format(filepath))

    if hasattr(py_mod, name):
        mod_inst = getattr(py_mod, name)
    else:
        raise RuntimeError("Loading function '{}' from '{}' failed".format(name, filepath))

    return mod_inst


def get_resource_content(package, filename):
    with pkg_resources.resource_stream(package, filename) as stream:
        return stream.read().decode('utf-8')


def exception_traceback(exc_info=None):
    """
    Return a string containing a traceback message for the given
    exc_info tuple (as returned by sys.exc_info()).

    from setuptools.tests.doctest
    """

    if not exc_info:
        exc_info = sys.exc_info()

    # Get a traceback message.
    excout = StringIO()
    exc_type, exc_val, exc_tb = exc_info
    traceback.print_exception(exc_type, exc_val, exc_tb, file=excout)
    return excout.getvalue()
