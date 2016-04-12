#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens@gmail.com>'
__copyright__ = 'Copyright 2016 JP Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib2
try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):
    ''' addrs: (chat_id, token, text) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    chat_id, token = item.addrs

    data = {
        'chat_id':              chat_id,
        'parse_mode':           'Markdown',
        'disable_notification': False,
        'text':                 item.message,
    }

    try:
        method = "POST"
        endpoint = "https://api.telegram.org/bot%s/sendMessage" % (token)

        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)

        request = urllib2.Request(endpoint, data=json.dumps(data))
        request.add_header("Content-Type",'application/json')

        connection = opener.open(request,timeout=5)

        reply = str(connection.read())
        srv.logging.debug("Telegram reply: %s" % reply)

        r = json.loads(reply)
        if 'ok' in r and r['ok']:
            return True

        return False

    except urllib2.HTTPError, e:
        srv.logging.warn("Failed to send POST request to Telegram using %s: %s" % (endpoint, str(e.read())))
        return False

    return True
