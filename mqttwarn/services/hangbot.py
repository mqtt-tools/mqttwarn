#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__    = 'Bram Hendrickx'
__copyright__ = 'Copyright 2016 Bram Hendrickx'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

Original script by Bram Hendrickx. https://github.com/mqtt-tools/mqttwarn/blob/main/mqttwarn/services/ifttt.py
Modified to work with hangoutsbot api plugin https://github.com/hangoutsbot/hangoutsbot/wiki/API-Plugin
"""

__author__    = 'Michael Brougham'
__copyright__ = 'Copyright 2018 Michael Brougham'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'


import json
import requests


def plugin(srv, item):
    """ expects (url,port,apikey, convid) in addrs """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    payload = {
        'key': item.addrs[2],
        'sendto': item.addrs[3],
        'content': item.message
    }
    try:
        srv.logging.debug("Sending to hangoutsbot")
        url = "https://" + item.addrs[0] + ":" + item.addrs[1]
        headers = {'content-type': 'application/json'}
        requests.post(url, data = json.dumps(payload), headers = headers, verify=False)
        srv.logging.debug("Successfully sent to hangoutsbot")
    except Exception as e:
        srv.logging.warning("Failed to send message to hangoutsbot" % e)
        return False

    return True
