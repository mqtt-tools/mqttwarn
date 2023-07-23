# -*- coding: utf-8 -*-
# (c) 2014-2023 The mqttwarn developers
import ast
import codecs
import logging
import os
import re
import sys
import typing as t
from configparser import Interpolation, NoOptionError, NoSectionError, RawConfigParser

from mqttwarn.util import load_functions

HAVE_TLS = True
try:
    import ssl
except ImportError:
    HAVE_TLS = False


logger = logging.getLogger(__name__)


def expand_vars(input: str, sources: t.Dict[str, t.Callable[[str], str]]) -> str:
    """
    Expand variables in `input` string with values from `sources` dict.

    Variables may be in two forms, either $TYPE:KEY or ${TYPE:KEY}. The second form must be used when `KEY` contains
    characters other than numbers, alphabets or underscore. Supported `TYPE`s depends on keys of `sources` dict.

    The `sources` is a dict where key is name of `TYPE` in the pattern above and value is a function that takes `KEY`
    as argument and returns contents of the variable to be expanded.

    :return: Input string with variables expanded
    """
    expanded = ""
    input_index = 0
    match = None
    # `input` may have multiple variables in form of $TYPE:KEY or ${TYPE:KEY} pattern, iterate through them
    for match in re.finditer(r"\$(\w+):(\w+)|\$\{(\w+):([^}]+)\}", input):
        var_type = match[1] if match[1] else match[3]  # TYPE part in the variable pattern
        var_key = match[2] if match[2] else match[4]  # KEY part in the variable pattern

        if var_type not in sources:
            raise KeyError(f"{match[0]}: Variable type '{var_type}' not supported")
        source = sources[var_type]

        try:
            value = source(var_key)
        except Exception as ex:
            raise KeyError(f"{match[0]}: {str(ex)}") from ex

        match_start, match_end = match.span()
        expanded += input[input_index:match_start] + value
        input_index = match_end

    if match:
        return expanded + input[input_index:]
    return input


class VariableInterpolation(Interpolation):
    def __init__(self, configuration_path):
        self.configuration_path = configuration_path
        self.sources = {
            "ENV": self.get_env_variable,
            "FILE": self.get_file_contents,
        }

    def before_get(self, parser, section, option, value, defaults):
        return expand_vars(value, self.sources) if type(value) == str else value

    def get_env_variable(self, name: str) -> str:
        """
        Get environment variable of `name` and return it
        """
        return os.environ[name]

    def get_file_contents(self, filepath: str) -> str:
        """
        Get file contents from `filepath` and return it
        """
        if not os.path.isfile(filepath):
            # Read file contents relative to path of configuration file if path is relative
            filepath = os.path.join(self.configuration_path, filepath)
        with open(filepath) as file:
            return file.read()


class Config(RawConfigParser):

    specials: t.Dict[str, t.Union[bool, None]] = {
        "TRUE": True,
        "FALSE": False,
        "NONE": None,
    }

    def __init__(self, configuration_file: t.Optional[str] = None, defaults: t.Optional[t.Dict] = None):

        defaults = defaults or {}

        self.configuration_path = None

        configuration_path = os.path.dirname(configuration_file) if configuration_file else None
        RawConfigParser.__init__(self, interpolation=VariableInterpolation(configuration_path))
        if configuration_file is not None:
            f = codecs.open(configuration_file, "r", encoding="utf-8")
            self.read_file(f)
            f.close()

            self.configuration_path = configuration_path

        """ set defaults """
        self.hostname = "localhost"
        self.port = 1883
        self.username = None
        self.password = None
        self.clientid = None
        self.lwt = None
        self.lwt_alive = None
        self.skipretained = False
        self.cleansession = False
        self.protocol = 3

        self.logformat = "%(asctime)-15s %(levelname)-8s [%(name)-26s] %(message)s"
        self.logfile = "stream://sys.stderr"
        self.loglevel = "DEBUG"

        self.filteredmessagesloglevel = "INFO"

        self.functions = None
        self.num_workers = 1

        self.ca_certs = None
        self.tls_version = None
        self.certfile = None
        self.keyfile = None
        self.tls_insecure = False
        self.tls = False

        self.__dict__.update(defaults)
        self.__dict__.update(self.config("defaults"))

        if HAVE_TLS is False:
            logger.error("TLS parameters set but no TLS available (SSL)")
            # TODO: Review this.
            sys.exit(2)

        if self.ca_certs is not None:
            self.tls = True

        if self.tls_version is not None:
            if self.tls_version == "tlsv1_2":
                self.tls_version = ssl.PROTOCOL_TLSv1_2
            if self.tls_version == "tlsv1_1":
                self.tls_version = ssl.PROTOCOL_TLSv1_1
            if self.tls_version == "tlsv1":
                self.tls_version = ssl.PROTOCOL_TLSv1

        self.loglevelnumber = self.level2number(self.loglevel)
        self.filteredmessagesloglevelnumber = self.level2number(self.filteredmessagesloglevel)

        if self.functions is not None and self.functions.strip() != "":

            logger.info("Loading user-defined functions from %s" % self.functions)

            # Load function file as given.
            if os.path.isfile(self.functions):
                functions_file = self.functions

            # Load function file relative to path of configuration file if path is relative.
            else:
                functions_file = os.path.join(self.configuration_path, self.functions)

            self.functions = load_functions(functions_file)

    def level2number(self, level: str) -> int:

        levels = {
            "CRITICAL": 50,
            "DEBUG": 10,
            "ERROR": 40,
            "FATAL": 50,
            "INFO": 20,
            "NOTSET": 0,
            "WARN": 30,
            "WARNING": 30,
        }

        return levels.get(level.upper(), levels["DEBUG"])

    def g(self, section: str, key: str, default=None) -> t.Any:
        val = None
        try:
            val = self.get(section, key)
            if isinstance(val, str) and val.upper() in self.specials:
                return self.specials[val.upper()]
            return ast.literal_eval(val)
        except (NoOptionError, NoSectionError):
            return default
        except ValueError:  # e.g. %(xxx)s in string
            return val
        except SyntaxError:  # If not python value, e.g. list of targets coma separated
            return val
        except:
            raise

    def getlist(self, section: str, key: str) -> t.Union[t.List, None]:
        """Return a list, fail if it isn't a list"""

        val = None
        try:
            val_str = self.get(section, key)
            val = [s.strip() for s in val_str.split(",")]
        except Exception as e:
            logger.warning("Expecting a list in section `%s', key `%s' (%s)" % (section, key, e))

        return val

    # TODO: Add return type annotation.
    def getdict(self, section: str, key: str):
        val = self.g(section, key)

        try:
            return dict(val)
        except:
            return None

    def config(self, section: str) -> t.Dict:
        """Convert a whole section's options (except the options specified
        explicitly below) into a dict, turning

            [config:mqtt]
            host = 'localhost'
            username = None
            list = [1, 'aaa', 'bbb', 4]

        into

            {'username': None, 'host': 'localhost', 'list': [1, 'aaa', 'bbb', 4]}

        Cannot use config.items() because I want each value to be
        retrieved with g() as above"""

        if self.has_section(section):
            return dict(
                (key, self.g(section, key)) for (key) in self.options(section) if key not in ["targets", "module"]
            )
        else:
            if section == "defaults":
                return {}
            else:
                raise KeyError(f"Configuration section does not exist: {section}")


def load_configuration(configfile: t.Optional[str] = None, name: str = "mqttwarn") -> Config:

    if configfile is None:
        configfile = str(os.getenv(name.upper() + "INI", name + ".ini"))

    if not os.path.exists(configfile):
        raise FileNotFoundError('Configuration file "{}" does not exist'.format(configfile))

    # TODO: There should be a factory method which creates a `Config` instance,
    #       including defaults, but without loading a configuration file.
    defaults: t.Dict[str, str] = {
        "clientid": name,
        "lwt": "clients/{}".format(name),
        "lwt_alive": "1",
        "lwt_dead": "0",
    }

    return Config(configfile, defaults=defaults)
