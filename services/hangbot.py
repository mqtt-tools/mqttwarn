#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Bram Hendrickx'
__copyright__ = 'Copyright 2016 Bram Hendrickx'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

''' Modified ifttt.py to work with hangoutsbot api plugin https://github.com/hangoutsbot/hangoutsbot/wiki/API-Plugin '''

import json
import requests

def plugin(srv, item):
    ''' expects (url,port,apikey, convid) in addrs '''

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
        srv.logging.debug("Successfully sent ifttt event")
    except Exception, e:
        srv.logging.warning("Cannot send ifttt event: %s" % (str(e)))
        return False

    return True
