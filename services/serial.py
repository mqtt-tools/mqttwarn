#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Daniel Lindner <andann83()gmail.com>'
__copyright__ = 'Copyright 2016 Daniel Lindner'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import serial

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # item.config is brought in from the configuration file
    config   = item.config

    # addrs is a list[] associated with a particular target.
    # While it may contain more than one item (e.g. pushover)
    # the `file' service carries one only, i.e. a path name
    try:
        comName = item.addrs[0].format(**item.data).encode('utf-8')
        comBaudRate = int(item.addrs[1])
    except:
        srv.logging.error("Incorrect target configuration for {0}/{1}".format(item.service, item.target))
        return False

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    # If format specifies the hex keyword try to transform bytes from hex
    test = text[:5]
    if test == ":HEX:":
        text = bytes(bytearray.fromhex(text[5:]))

    if type(config) == dict and 'append_newline' in config and config['append_newline']:
        text = text + "\n"

    try:
        ser = serial.Serial(comName, comBaudRate)
        if ser.is_open:
            ser.write(text)
            ser.close
    except SerialException, e:
        srv.logging.warning("Cannot write to com port `%s': %s" % (comName, str(e)))
        return False

    return True
