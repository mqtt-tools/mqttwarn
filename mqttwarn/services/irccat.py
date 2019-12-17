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
        srv.logging.warn("Incorrect target configuration")
        return False

    message = item.message

    color = None
    priority = item.priority
    if priority == 1:
        color = '%GREEN'
    if priority == 2:
        color = '%RED'

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        if color is not None:
            sock.send(color)
        sock.send(message)
        sock.close()

    except Exception as e:
        srv.logging.error("Error sending IRCCAT notification to %s:%s [%s]: %s" % (item.target, addr, port, e))
        return False

    return True
