#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import time
import socket


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

    try:
        parts = text.split()
    except:
        srv.logging.error("target `carbon': cannot split string")
        return False

    if len(parts) == 1:
        metric_name = item.data.get('topic', 'ohno').replace('/', '.')
        value = parts[0]
        tics = int(time.time())
    else:
        if len(parts) == 2:
            metric_name = parts[0]
            value = parts[1]
            tics = int(time.time())
        else:
            if len(parts) == 3:
                metric_name = parts[0]
                value = parts[1]
                tics = int(parts[2])

    if metric_name.startswith('.'):     # omit dot there caused by useless leading slash in topic
        metric_name = metric_name[1:]
    carbon_msg = "%s %s %d" % (metric_name, value, tics)
    srv.logging.debug("Sending to carbon: %s" % (carbon_msg))
    carbon_msg = carbon_msg + "\n"
    try:
        sock = socket.socket()
        sock.connect((carbon_host, carbon_port))
        sock.sendall(carbon_msg)
        sock.close()
    except Exception as e:
        srv.logging.warning("Cannot send to carbon service %s:%d: %s" % (carbon_host, carbon_port, e))
        return False

    return True
