#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Diogo Gomes <diogogomes()gmail.com>'
__copyright__ = 'Copyright 2014 Diogo Gomes'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib2
import base64
try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):
    ''' addrs: (node, name) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    appid = item.config['appid']
    appsecret = item.config['appsecret']

    data = dict()
    data["event"] = item.addrs[0]
    data["trackers"]  = item.addrs[1]

    try:
        method = "POST"
        resource = "https://api.instapush.im/v1/post"

        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)

        request = urllib2.Request(resource, data=json.dumps(data))
        request.add_header('x-instapush-appid', appid)
        request.add_header('x-instapush-appsecret', appsecret)
        request.add_header("Content-Type",'application/json')

        connection = opener.open(request)
	reply = str(connection.read())
        r = json.loads(reply)

	srv.logging.debug("Server reply: %s" % reply)
	srv.logging.info("%s: %s" % (item.target, r['msg']))

        return not r['error']

    except Exception, e:
        srv.logging.warn("Failed to send POST request to instapush using %s: %s" % (resource, str(e)))
        return False

    return True
