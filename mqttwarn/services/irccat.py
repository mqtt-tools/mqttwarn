#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import socket


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        addr, port, channel = item.addrs
    except:
        srv.logging.warning("Incorrect target configuration")
        return False

    message = item.message

    # Optionally apply coloring.
    color = None
    if item.priority == 1:
        color = '%GREEN'
    elif item.priority == 2:
        color = '%RED'
    if color is not None:
        message = color + message

    srv.logging.debug("Sending to IRCcat: %s" % (message))

    # Apparently, a trailing newline is needed.
    # https://github.com/mqtt-tools/mqttwarn/issues/547#issuecomment-944632712
    message += "\n"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        sock.send(message.encode())
        sock.close()

    except Exception as e:
        srv.logging.error("Error sending IRCcat notification to %s:%s [%s]: %s" % (item.target, addr, port, e))
        return False

    return True
