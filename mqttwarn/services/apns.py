#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import json
try:
    from apns import APNs, Payload
except:
    pass


def plugin(srv, item):
    addrs = item.addrs
    data = item.data
    text = item.message

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        cert_file, key_file = addrs
    except:
        srv.logging.warning("Incorrect service configuration")
        return False

    if 'apns_token' not in data:
        srv.logging.warning("Cannot notify via APNS: apns_token is missing")
        return False

    apns_token = data['apns_token']

    custom = {}
    try:
        payload = data['payload']
        mdata = json.loads(payload)
        if 'custom' in mdata:
            custom = mdata['custom']
    except:
        pass

    apns = APNs(use_sandbox=False, cert_file=cert_file, key_file=key_file)

    pload = Payload(alert=text, custom=custom, sound="default", badge=1)
    apns.gateway_server.send_notification(apns_token, pload)

    srv.logging.debug("Successfully published APNS notification to %s" % apns_token)

    return True
