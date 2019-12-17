#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Diogo Gomes <diogogomes()gmail.com>'
__copyright__ = 'Copyright 2014 Diogo Gomes'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()
from builtins import str

import urllib.request, urllib.error, urllib.parse
try:
    import simplejson as json
except ImportError:
    import json


def plugin(srv, item):
    """ addrs: (node, name) """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    appid = item.config['appid']
    appsecret = item.config['appsecret']
    data = dict()
    data["event"] = item.addrs[0]
    if len(item.addrs) > 1:
        data["trackers"] = item.addrs[1]
    else:
        data["trackers"]  = json.loads(item.message)
    for key in list(data["trackers"].keys()):
        try:
            data["trackers"][key] = data["trackers"][key].format(**item.data).encode('utf-8')
        except Exception as e:
            srv.logging.debug("Parameter %s cannot be formatted: %s" % (key, e))
            return False
    try:
        method = "POST"
        resource = "https://api.instapush.im/v1/post"

        handler = urllib.request.HTTPHandler()
        opener = urllib.request.build_opener(handler)

        request = urllib.request.Request(resource, data=json.dumps(data))
        request.add_header('x-instapush-appid', appid)
        request.add_header('x-instapush-appsecret', appsecret)
        request.add_header("Content-Type",'application/json')

        connection = opener.open(request, timeout=5)

        reply = str(connection.read())
        srv.logging.info("Server reply: %s" % reply)

        r = json.loads(reply)
        srv.logging.info("%s: %s" % (item.target, r['msg']))

        return not r['error']

    except urllib.error.HTTPError as e:
        srv.logging.warn("Failed to send POST request to instapush using %s: %s" % (resource, str(e.read())))
        return False

    return True
