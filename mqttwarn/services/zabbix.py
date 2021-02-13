#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

try:
    import simplejson as json
except ImportError:
    import json
from mqttwarn.vendor import ZabbixSender
import time


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        trapper, port = item.addrs
    except:
        srv.logging.error("Module target is incorrectly configured")
        return False

    host = item.config.get('host', 'MQTT_BUS')
    discovery_key = item.config.get('discovery_key', 'mqtt.discovery')

    client = item.data.get('client', None)
    if client is None:
        srv.logging.warn("No client in item; ignoring")
        return False

    # If status_key is in item (set by function ZabbixData()), then we have to
    # add a host to Zabbix LLD, and the value of the message is 0/1 to indicate
    # host down/up
    status_key = item.data.get('status_key', None)
    if status_key is not None:
        status = item.message

        clients = []
        clients.append( { '{#MQTTHOST}' : client } )

        # {"data": [{"{#MQTTHOST}": "jog02"}]}
        lld_payload = json.dumps(dict(data = clients))

        try:
            # Add LLD for the client host to Zabbix
            sender = ZabbixSender.ZabbixSender(trapper, server_port = int(port))
            sender.AddData(host=host, key=discovery_key, value=lld_payload)
            res = sender.Send()
            sender.ClearData()

            if res and 'info' in res:
                srv.logging.debug("Trapper for LLD responds with %s" % res['info'])

                # Add status to the "status key". This must not happen too early,
                # or Zabbix will fail this value if the LLD for the host hasn't
                # been recorded. Attempt a sleep. FIXME
                time.sleep(3)  # FIXME
                sender.AddData(host=client, key=status_key, value=status)
                res = sender.Send()
                sender.ClearData()
                if res and 'info' in res:
                    srv.logging.debug("Trapper for STATUS responds with %s" % res['info'])

                return True
        except Exception as e:
            srv.logging.warn("Trapper responded: %s" % e)
            return False

    # We are adding a normal item/value via the trapper
    key = item.data.get('key', None)
    if client is None or key is None:
        srv.logging.warn("Client or Key missing in item; ignoring")
        return False

    value = item.message

    try:
        # Send item/value for host to the trapper
        sender = ZabbixSender.ZabbixSender(trapper, server_port = int(port))
        sender.AddData(host=client, key=key, value=value)
        res = sender.Send()
        sender.ClearData()

        if res and 'info' in res:
            srv.logging.debug("Trapper for client=%s, item=%s, value=%s responds with %s" % (client, key, value, res['info']))

            return True
    except Exception as e:
        srv.logging.warn("Trapper responded: %s" % e)

    return False
