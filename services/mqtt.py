#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import paho.mqtt.publish as mqtt  # pip install --upgrade paho-mqtt

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    config   = item.config

    hostname    = config.get('hostname', 'localhost')
    port        = int(config.get('port', '1883'))
    qos         = int(config.get('qos', 0))
    retain      = int(config.get('retain', 0))
    username    = config.get('username', None)
    password    = config.get('password', None)

    auth = None

    if username is not None:
        auth = {
            'username' : username,
            'password' : password
        }

    outgoing_topic =  item.addrs[0]

    # Attempt to interpolate data into topic name. If it isn't possible
    # ignore, and return without publish

    if item.data is not None:
        try:
            outgoing_topic =  item.addrs[0].format(**item.data).encode('utf-8')
        except:
            srv.logging.debug("Outgoing topic cannot be formatted; not published")
            return False

    outgoing_payload = item.message

    try:
        mqtt.single(outgoing_topic, outgoing_payload,
            qos=qos,
            retain=retain,
            hostname=hostname,
            port=port,
            auth=auth)
    except Exception, e:
        srv.logging.warning("Cannot PUBlish via `mqtt:%s': %s" % (item.target, str(e)))
        return False

    return True
