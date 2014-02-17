#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def plugin(srv, item):
    ''' Publish via MQTT to the same broker connection.
        Requires topic, qos and retain flag '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    outgoing_topic =  item.addrs[0]
    qos  =  item.addrs[1]
    retain = item.addrs[2]

    # Attempt to interpolate data into topic name. If it isn't possible
    # ignore, and return without publish

    if item.data is not None:
        try:
            outgoing_topic =  item.addrs[0].format(**item.data).encode('utf-8')
        except:
            srv.logging.debug("Outgoing topic cannot be formatted; not published")
            return

    outgoing_payload = item.message

    try:
        srv.mqttc.publish(outgoing_topic, outgoing_payload, qos=qos, retain=retain)
    except Exception, e:
        srv.logging.warning("Cannot PUBlish via `mqttpub:%s': %s" % (item.target, str(e)))
    return
