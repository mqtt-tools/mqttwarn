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
import time

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        trapper, port = item.addrs
    except:
        srv.logging.error("Module target is incorrectly configured")
        return False

    client = item.data.get('client', None)
    if client is None:
        srv.logging.warn("No client in item; ignoring")
        return False

    # status will be "1" or "0", depending on whether client has come up or has died
    status = item.message

    clients = []

    clients.append( { '{#MQTTHOST}' : client } )

    # {"data": [{"{#MQTTHOST}": "jog02"}]}
    lld_payload = json.dumps(dict(data = clients))

    try:
        # Add LLD for the client host to Zabbix
        sender = ZabbixSender.ZabbixSender(trapper, server_port = int(port))
        sender.AddData(host='MQTT_BUS', key='mqtt.discovery', value=lld_payload)
        res = sender.Send()
        sender.ClearData()

        if res and 'info' in res:
            srv.logging.debug("Trapper for LLD responds with %s" % res['info'])

            # Add status to the "status key". This must not happen too early,
            # or Zabbix will fail this value if the LLD for the host hasn't
            # been recorded. Attempt a sleep. FIXME
            time.sleep(3)
            sender.AddData(host=client, key=status_key, value=status)
            res = sender.Send()
            sender.ClearData()
            if res and 'info' in res:
                srv.logging.debug("Trapper for STATUS responds with %s" % res['info'])

            return True
    except Exception, e:
        srv.logging.warn("Trapper responded: %s" % (str(e)))

    return False
