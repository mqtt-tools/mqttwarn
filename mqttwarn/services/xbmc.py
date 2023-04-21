#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()

import urllib.request, urllib.parse, urllib.error
import base64
try:
    import simplejson as json
except ImportError:
    import json  # type: ignore[no-redef]


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    xbmchost = item.addrs[0]
    xbmcusername = None
    xbmcpassword = None

    if len(item.addrs) == 3:
        xbmcusername = item.addrs[1]
        xbmcpassword = item.addrs[2]

    title    = item.title
    message  = item.message
    image    = item.image

    jsonparams = {
        "jsonrpc" : "2.0",
        "method"  : "GUI.ShowNotification",
        "id"      : 1,
        "params"  : {
            "title"       : title,
            "message"     : message,
            "image"       : image,
            "displaytime" : 10000
        }
    }
    jsoncommand = json.dumps(jsonparams).encode("utf-8")

    url = 'http://%s/jsonrpc' % (xbmchost)
    try:
        srv.logging.debug("Sending XBMC notification to %s [%s]..." % (item.target, xbmchost))
        req = urllib.request.Request(url, jsoncommand)
        req.add_header("Content-type", "application/json")
        if xbmcpassword is not None:
            credentials = '%s:%s' % (xbmcusername, xbmcpassword)
            basicauth_token = base64.b64encode(credentials.encode('utf-8')).decode()
            authheader = "Basic %s" % basicauth_token
            req.add_header("Authorization", authheader)
        response = urllib.request.urlopen(req, timeout = 2)
        srv.logging.debug("Successfully sent XBMC notification")
    except urllib.error.URLError as e:
        srv.logging.error("URLError: %s" % e)
        return False
    except Exception as e:
        srv.logging.error("Error sending XBMC notification to %s [%s]: %s" % (item.target, xbmchost, e))
        return False

    return True
