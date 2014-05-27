#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

try:
    import json
except ImportError:
    import simplejson as json
from vendor import ZabbixSender

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        trapper, port = item.addrs
    except:
        srv.logging.error("Module target is incorrectly configured")
        return False

    client = item.data.get('client', None)
    key = item.data.get('key', None)
    if client is None or key is None:
        srv.logging.warn("Client or Key missing in item; ignoring")
        return False

    value = item.message

    try:
        # Add LLD for the client host to Zabbix
        sender = ZabbixSender.ZabbixSender(trapper, server_port = int(port))
        sender.AddData(host=client, key=key, value=value)
        res = sender.Send()
        sender.ClearData()

        if res and 'info' in res:
            srv.logging.debug("Trapper for item=%s, value=%s responds with %s" % (key, value, res['info']))

            return True
    except Exception, e:
        srv.logging.warn("Trapper responded: %s" % (str(e)))

    return False
