#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib
import urllib2

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    xbmchost = item.addrs
    title    = item.title
    message  = item.message

    command = '{"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"%s","message":"%s"},"id":1}' % (title, message)
    command = command.encode('utf-8')
    url = 'http://%s/jsonrpc' % (xbmchost)
    try:
        srv.logging.debug("Sending XBMC notification to %s [%s]..." % (item.target, xbmchost))
        req = urllib2.Request(url, command)
        req.add_header("Content-type", "application/json")
        response = urllib2.urlopen(req)
        srv.logging.debug("Successfully sent XBMC notification")
    except urllib2.URLError, e:
        srv.logging.error("URLError: %s" % (str(e)))
    except Exception, e:
        srv.logging.error("Error sending XBMC notification to %s [%s]: %s" % (item.target, xbmchost, str(e)))
