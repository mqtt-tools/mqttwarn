#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Daniel Lindner <andann83()gmail.com>'
__copyright__ = 'Copyright 2016 Daniel Lindner'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import serial
from builtins import bytes

_serialport = None


def plugin(srv, item):
    global _serialport
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # item.config is brought in from the configuration file
    config   = item.config

    # addrs is a list[] associated with a particular target.
    # While it may contain more than one item (e.g. pushover)
    # the `serial' service carries one two, i.e. a com name and baudrate
    try:
        comName = item.addrs[0].format(**item.data)
        comBaudRate = int(item.addrs[1])
    except:
        srv.logging.error("Incorrect target configuration for {0}/{1}".format(item.service, item.target))
        return False

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    # If message specifies the hex keyword try to transform bytes from hex
    # else send string as it is
    test = text[:5]
    if test == ":HEX:":
        text = bytes(bytearray.fromhex(text[5:]))

    # Append newline if config option is set
    if type(config) == dict and 'append_newline' in config and config['append_newline']:
        text = text + "\n"

    try:
        try:
            if callable(getattr(_serialport, "is_open", None)):
                _serialport.is_open
            else:
                _serialport.isOpen
            srv.logging.debug("%s already open", comName)
        except:
            #Open port for first use
            srv.logging.debug("Open %s with %d baud", comName, comBaudRate)
            _serialport = serial.serial_for_url(comName)
            _serialport.baudrate = comBaudRate

        _serialport.write(text.encode('utf-8'))

    except serial.SerialException as e:
        srv.logging.warning("Cannot write to com port `%s': %s" % (comName, e))
        return False

    return True

