#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Leonardo Rizzi <l.rizzi()wide-net.org>'
__copyright__ = 'Copyright 2017 Leonardo Rizzi'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):
    ''' addrs: (token, roomid, color, notify) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    token   = item.addrs[0]
    roomid  = item.addrs[1]
    color   = item.addrs[2]
    notify  = item.addrs[3]
    timeout = item.config.get('timeout', 60)
    server  = item.config.get('server', 'api.hipchat.com')

    url = 'https://' + str(server) + '/v2/room/' + str(roomid) + '/notification'
    message  = item.message

    try:
        headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % token}

        datastr = json.dumps({
                'message': message,
                'color': color,
                'message_format': 'html',
                'notify': notify})

	request = urllib2.Request(url, headers=headers, data=datastr)
        resp = urllib2.urlopen(request, timeout=timeout)
        data = resp.read()
        print "POST returns ", data
    except Exception, e:
            srv.logging.warn("Cannot POST %s: %s" % (url, str(e)))
            return False

    return True
