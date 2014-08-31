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
    ''' addrs: (node, name) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    url     = item.config['url']
    apikey  = item.config['apikey']
    timeout = item.config['timeout']

    node  = item.addrs[0]
    name  = item.addrs[1]

    try:
        value = float(item.payload)
    except ValueError:
        srv.logging.warn("Unable to process message payload as it is not a number: %s" % (str(e)))
        return False

    try:
        params = { 'apikey': apikey, 'node': node, 'json': json.dumps({ name : value }) }
        resource = url + '/input/post.json?' + urllib.urlencode(params)

        request = urllib2.Request(resource)
        request.add_header('User-agent', srv.SCRIPTNAME)

        response = urllib2.urlopen(request, timeout=timeout)
        data = response.read()
    except Exception, e:
        srv.logging.warn("Failed to send GET request to EmonCMS using %s: %s" % (resource, str(e)))
        return False

    return True
