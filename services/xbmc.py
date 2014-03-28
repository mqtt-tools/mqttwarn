#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib
import urllib2
import base64
try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        xbmchost, xbmcusername, xbmcpassword  = item.addrs
    except:
        xbmchost = item.addrs


    title    = item.title
    message  = item.message

    jsonparams = {
        "jsonrpc" : "2.0",
        "method"  : "GUI.ShowNotification",
        "id"      : 1,
        "params"  : {
            "title"   : title,
            "message" : message
        }
    }
    jsoncommand = json.dumps(jsonparams)

    url = 'http://%s/jsonrpc' % (xbmchost)
    try:
        srv.logging.debug("Sending XBMC notification to %s [%s]..." % (item.target, xbmchost))
        req = urllib2.Request(url, jsoncommand)
        req.add_header("Content-type", "application/json")
        if xbmcpassword:
            base64string = base64.encodestring ('%s:%s' % (xbmcusername, xbmcpassword))[:-1]
            authheader = "Basic %s" % base64string
            req.add_header("Authorization", authheader)
	    srv.logging.debug("Adding XBMC authentication header")
	else:
	    srv.logging.debug("Not adding XBMC authentication header")	
        response = urllib2.urlopen(req)
        srv.logging.debug("Successfully sent XBMC notification")
    except urllib2.URLError, e:
        srv.logging.error("URLError: %s" % (str(e)))
        return False
    except Exception, e:
        srv.logging.error("Error sending XBMC notification to %s [%s]: %s" % (item.target, xbmchost, str(e)))
        return False

    return True
