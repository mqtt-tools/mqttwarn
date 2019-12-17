#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Stefan Roellin <stefan()roellin-baumann.ch>'
__copyright__ = 'Copyright 2015 Stefan Roellin'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()

import http.client, urllib.request, urllib.parse, urllib.error


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    data = {'Message': item.message.encode('utf-8'),
            'Origin': item.title,
            'Timeout': item.config.get('timeout', 5),
            'Address': item.addrs[1],
            'Progress': -1
            }
    if item.image != None:
        data['Image'] = item.image

    http_handler = http.client.HTTPConnection(item.addrs[0])

    try:
        http_handler.request("POST", 'Myth/SendNotification',
                             headers={'Content-type': "application/x-www-form-urlencoded", "Accept": "text/plain"},
                             body=urllib.parse.urlencode(data))
    except (SSLError, HTTPException) as e:
        srv.logging.warn("mythtv notification failed: %s" % e)
        return False            

    response = http_handler.getresponse()

    srv.logging.debug("Reponse: %s, %s" % (response.status, response.reason))

    return True 
