# -*- coding: utf-8 -*-
# (c) 2014-2018 The mqttwarn developers
import os
import sys
import signal
import logging

from mqttwarn.configuration import Config
from mqttwarn.core import bootstrap, connect, cleanup

logger = logging.getLogger(__name__)


def run():
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


def load_configuration(configfile=None, name=None):
    if configfile is None:
        configfile = os.getenv(name.upper() + 'INI', name + '.ini')

    if not os.path.exists(configfile):
        raise ValueError('Configuration file "{}" does not exist'.format(configfile))

    defaults = {
        'clientid': name,
        'lwt': 'clients/{}'.format(name),
        'logfile': os.getenv(name.upper() + 'INI', name + '.ini'),
    }

    return Config(configfile, defaults=defaults)


def setup_logging(config):
    LOGLEVEL = config.loglevelnumber
    LOGFILE = config.logfile
    LOGFORMAT = config.logformat

    # Send log messages to sys.stderr by configuring "logfile = stream://sys.stderr"
    if LOGFILE.startswith('stream://'):
        LOGFILE = LOGFILE.replace('stream://', '')
        logging.basicConfig(stream=eval(LOGFILE), level=LOGLEVEL, format=LOGFORMAT)

    # Send log messages to file by configuring "logfile = 'mqttwarn.log'"
    else:
        logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
