#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Klaudiusz Staniek <kstaniek at gmail.com>'
__copyright__ = 'Copyright 2015 Klaudiusz Staniek'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib2
try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):
    """ addrs: ("widgets|dashboards", name|*

        for widgets:
            message: json string with field accepted by dashboard
        for dashboard:
            message: { "action": "reload" } this is the only action implemented in dashing

        Sample config:
        [config:dashing]
        hostname = 'dashboard.home.local'
        port = 3030
        auth_token = 'YOUR_AUTH_TOKEN'
        timeout = 5
        targets = {
            'outside_temp': [ "widgets", "klimato" ],   # target for specific widget "klimato"
            'widgets': [ "widgets" ],                   # target for widget where last topic part is a widget name
            'dashboards': [ "dashboards", "*" ],        # target for all dashboards
            }
    """

    srv.logging.debug("*** MODULE={}: service={}, target={}".format(__file__, item.service, item.target))

    config = item.config
    hostname = config.get('hostname', 'localhost')
    port = int(config.get('port', '3030'))
    timeout = item.config.get('timeout', 10)
    auth_token = item.config.get('auth_token', 'YOUR_AUTH_TOKEN')

    trg_len = len(item.addrs)
    if trg_len > 0 and item.addrs[0] in ['widgets', 'dashboards']:
        target = item.addrs[0]
        if trg_len == 1:
            param = item.topic.split('/')[-1]
        elif trg_len == 2:
            param = item.addrs[1]
        else:
            srv.logging.error("*** MODULE={}: Incorrect number of parameters: {}".format(__file__, item.target))
            return False
    else:
        srv.logging.error("*** MODULE={}: Incorrect target configuration: {}".format(__file__, item.target))
        return False

    url = "http://{}:{}/{}/{}".format(hostname, port, target, param)
    srv.logging.debug("*** MODULE={}: URL: {}".format(__file__, url))
    try:
        msg = json.loads(item.message)
    except:
        srv.logging.debug("*** MODULE={{: Payload not in JSON format: {}".format(__file__, item.message))
        # If no JSON then sending message formatted in JSON as value by default
        msg = {'value': str(item.message)}

    srv.logging.debug("*** MODULE={}: (auth_token omitted) DATA: {}".format(__file__, msg))
    msg['auth_token'] = auth_token
    data = json.dumps(msg)
    try:
        req = urllib2.Request(url, data, {'Content-Type': 'application/json', 'Content-Length': len(data)})
        f = urllib2.urlopen(req, timeout=timeout)
    except urllib2.URLError as e:
        srv.logging.error("*** MODULE={}: Wrong hostname or port for dashing service".format(__file__))
        return False
    except:
        srv.logging.exception("*** MODULE={}: Unhandled error when sending data to dashboard".format(__file__))
        return False

    f.close()
    return True
