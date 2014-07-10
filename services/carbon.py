#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import socket
import time

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # item.config is brought in from the configuration file
    config   = item.config

    # addrs is a list[] associated with a particular target.

    try:
        carbon_host, carbon_port = item.addrs
        carbon_port = int(carbon_port)
    except:
        srv.logging.error("Configuration for target `carbon' is incorrect")
        return False

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    metric_name = item.data.get('topic', 'ohno').replace('/', '.')
    carbon_msg = "%s %s %d\n" % (metric_name, text, int(time.time()))
    try:
        sock = socket.socket()
        sock.connect((carbon_host, carbon_port))
        sock.sendall(carbon_msg)
        sock.close()
    except Exception, e:
        srv.logging.warning("Cannot send to carbon service %s:%d: %s" % (carbon_host, carbon_port, str(e)))
        return False

    return True
