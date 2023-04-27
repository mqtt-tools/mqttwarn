# -*- coding: utf-8 -*-
# (c) 2014-2023 The mqttwarn developers
from __future__ import print_function

import codecs
import json
import logging
import os
import signal
import sys
import typing as t

from docopt import docopt

from mqttwarn import __version__
from mqttwarn.configuration import Config, load_configuration
from mqttwarn.core import bootstrap, cleanup, run_plugin, subscribe_forever
from mqttwarn.util import get_resource_content

logger = logging.getLogger(__name__)

APP_NAME = "mqttwarn"


def run():
    """
    Usage:
      {program} [make-config]
      {program} [make-udf]
      {program} [--config=] [--config-file=] [--plugin=] [--options=] [--data=]
      {program} --version
      {program} (-h | --help)

    No options:
      mqttwarn will start as a service.

    Interactive options:
      [--config=]               Use configuration settings from JSON string
      [--config-file=]          Use configuration settings from JSON file
      [--plugin=]               The plugin name to load. This can either be a
                                full qualified Python package/module name or a
                                path to a Python file.
      [--options=]              Configuration options to propagate to the plugin entrypoint.
      [--data=]                 Data to propagate to the plugin entrypoint.

    Bootstrapping options:
      make-config               Dump configuration file blueprint to STDOUT,
                                suitable for redirecting into a configuration file.
      make-udf                  Dump blueprint for user-defined functions file to STDOUT,
                                suitable for redirecting into a `udf.py` file.

    Miscellaneous options:
      --version                 Show version information
      -h --help                 Show this screen

    """

    # Use generic commandline options schema and amend with current program name
    commandline_schema = run.__doc__.format(program=APP_NAME)

    # Read commandline options
    options = docopt(commandline_schema, version=APP_NAME + " " + __version__)

    # TODO: Review this. Why do we need it?
    utf8_writer = codecs.getwriter("utf-8")
    sys.stdout = utf8_writer(sys.stdout.buffer)

    if options["make-config"]:
        payload = get_resource_content("mqttwarn.examples", "basic/mqttwarn.ini")
        print(payload)

    elif options["make-udf"]:
        payload = get_resource_content("mqttwarn.examples", "basic/udf.py")
        print(payload)

    elif options["--plugin"] and options["--options"]:

        # Decode arguments
        arg_plugin = options["--plugin"]
        arg_options = options["--options"] and json.loads(options["--options"]) or {}
        arg_data = options["--data"] and json.loads(options["--data"]) or {}
        arg_config = None
        if "--config" in options and options["--config"] is not None:
            arg_config = json.loads(options["--config"])

        # Launch service plugin in standalone mode
        launch_plugin_standalone(
            arg_plugin, arg_options, arg_data, configfile=options.get("--config-file"), config_more=arg_config
        )

    # Run mqttwarn in service mode when no command line arguments are given
    else:
        run_mqttwarn(configfile=options["--config-file"])


def launch_plugin_standalone(
    plugin: str,
    options: t.Dict,
    data: t.Dict,
    configfile: t.Optional[str] = None,
    config_more: t.Optional[t.Dict] = None,
):

    # Optionally load configuration file
    does_not_exist = False
    scriptname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    try:
        config = load_configuration(configfile=configfile, name=scriptname)
    except FileNotFoundError:
        does_not_exist = True
        config = Config()
        section = "config:{}".format(plugin)
        config.add_section(section)

    # Optionally add additional config settings from command line.
    if config_more is not None:
        section = "config:{}".format(plugin)
        if not config.has_section(section):
            config.add_section(section)
        for key, value in config_more.items():
            config.set(section, key, value)

    # Setup logging
    setup_logging(config)
    if does_not_exist:
        logger.info('Configuration file "{}" does not exist, using default settings'.format(configfile))

    logger.info('Running service plugin "{}" with options "{}"'.format(plugin, options))

    # Launch service plugin
    run_plugin(config=config, name=plugin, options=options, data=data)


def run_mqttwarn(configfile: t.Optional[str] = None):

    # Script name (without extension) used as last resort fallback for config/logfile names
    scriptname = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    # Load configuration file
    config = load_configuration(configfile=configfile, name=scriptname)

    # Setup logging
    setup_logging(config)
    logger.info("Starting {}".format(scriptname))
    logger.info("Log level is %s" % logging.getLevelName(logger.getEffectiveLevel()))

    # Handle signals
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    # Bootstrap mqttwarn.core
    bootstrap(config=config, scriptname=scriptname)

    # Connect to broker and start listening
    subscribe_forever()


def setup_logging(config: Config):
    LOGLEVEL = config.loglevelnumber
    LOGFILE = config.logfile
    LOGFORMAT = config.logformat

    # Send log messages to sys.stderr by configuring "logfile = stream://sys.stderr"
    if not LOGFILE:
        pass

    elif LOGFILE.startswith("stream://"):
        LOGFILE = LOGFILE.replace("stream://", "")
        logging.basicConfig(stream=eval(LOGFILE), level=LOGLEVEL, format=LOGFORMAT)

    # Send log messages to file by configuring "logfile = 'mqttwarn.log'"
    else:
        logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
