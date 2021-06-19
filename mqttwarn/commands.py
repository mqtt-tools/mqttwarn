# -*- coding: utf-8 -*-
# (c) 2014-2019 The mqttwarn developers
from __future__ import print_function
import os
import sys
import json
import codecs
import signal
import logging

from docopt import docopt

from mqttwarn import __version__
from mqttwarn.configuration import load_configuration, Config
from mqttwarn.core import bootstrap, connect, cleanup, run_plugin
from mqttwarn.util import get_resource_content

logger = logging.getLogger(__name__)

APP_NAME = 'mqttwarn'


def run():
    """
    Usage:
      {program} [make-config]
      {program} [make-samplefuncs]
      {program} [--config=] [--config-file=] [--plugin=] [--options=]
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
      [--options=]              Configuration options to propagate to the plugin
                                entrypoint.

    Bootstrapping options:
      make-config               Dump configuration file blueprint to STDOUT,
                                suitable for redirecting into a configuration file.
      make-samplefuncs          Dump blueprint for custom functions file to STDOUT,
                                suitable for redirecting into a `samplefuncs.py` file.

    Miscellaneous options:
      --version                 Show version information
      -h --help                 Show this screen

    """

    # Use generic commandline options schema and amend with current program name
    commandline_schema = run.__doc__.format(program=APP_NAME)

    # Read commandline options
    options = docopt(commandline_schema, version=APP_NAME + ' ' + __version__)

    # Python2/3 string encoding compat - sigh.
    # https://stackoverflow.com/questions/2737966/how-to-change-the-stdin-and-stdout-encoding-on-python-2/58449987#58449987
    utf8_writer = codecs.getwriter('utf-8')
    if sys.version_info.major <= 2:
        sys.stdout = utf8_writer(sys.stdout)
    else:
        sys.stdout = utf8_writer(sys.stdout.buffer)

    if options['make-config']:
        payload = get_resource_content('mqttwarn.examples', 'basic/mqttwarn.ini')
        print(payload)

    elif options['make-samplefuncs']:
        payload = get_resource_content('mqttwarn.examples', 'basic/samplefuncs.py')
        print(payload)

    elif options['--plugin'] and options['--options']:

        # Decode arguments
        arg_plugin = options['--plugin']
        arg_options = json.loads(options['--options'])
        arg_config = None
        if "--config" in options and options['--config'] is not None:
            arg_config = json.loads(options['--config'])

        # Launch service plugin in standalone mode
        launch_plugin_standalone(arg_plugin, arg_options, configfile=options.get("--config-file"), config_more=arg_config)


    # Run mqttwarn in service mode when no command line arguments are given
    else:
        run_mqttwarn()


def launch_plugin_standalone(plugin, options, configfile=None, config_more=None):

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
        for key, value in config_more.items():
            config.set(section, key, value)

    # Setup logging
    setup_logging(config)
    if does_not_exist:
        logger.info('Configuration file "{}" does not exist, using default settings'.format(configfile))

    logger.info('Running service plugin "{}" with options "{}"'.format(plugin, options))

    # Launch service plugin
    run_plugin(config=config, name=plugin, options=options)


def run_mqttwarn():

    # Script name (without extension) used as last resort fallback for config/logfile names
    scriptname = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    # Load configuration file
    config = load_configuration(name=scriptname)

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
    connect()


def setup_logging(config):
    LOGLEVEL = config.loglevelnumber
    LOGFILE = config.logfile
    LOGFORMAT = config.logformat

    # Send log messages to sys.stderr by configuring "logfile = stream://sys.stderr"
    if not LOGFILE:
        pass

    elif LOGFILE.startswith('stream://'):
        LOGFILE = LOGFILE.replace('stream://', '')
        logging.basicConfig(stream=eval(LOGFILE), level=LOGLEVEL, format=LOGFORMAT)

    # Send log messages to file by configuring "logfile = 'mqttwarn.log'"
    else:
        logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
