#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Bram Hendrickx'
__copyright__ = 'Copyright 2016 Bram Hendrickx'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import requests


def plugin(srv, item):
    ''' expects (apikey, event) in adddrs '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    event_type = "device_iden"
    try:
        apikey, event = item.addrs
    except:
        try:
            apikey, event = item.addrs
        except:
            srv.logging.warn("ifttt target is incorrectly configured")
            return False

    payload = {}
    payload["value1"] = item.message

    try:
        srv.logging.debug("Sending ifttt event")
        url = "https://maker.ifttt.com/trigger/" + event + "/with/key/" + apikey
        requests.post(url, data=payload)
        srv.logging.debug("Successfully sent ifttt event")
    except Exception as e:
        srv.logging.warning("Cannot send ifttt event: %s" % e)
        return False

    return True
