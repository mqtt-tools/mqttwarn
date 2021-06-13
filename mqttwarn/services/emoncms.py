#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()
from builtins import str

import urllib.request, urllib.parse, urllib.error

try:
    import simplejson as json
except ImportError:
    import json


def plugin(srv, item):
    """ addrs: (node, name) """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    url     = item.config['url']
    apikey  = item.config['apikey']
    timeout = item.config['timeout']

    node  = item.addrs[0]
    name  = item.addrs[1]
    value = item.payload

    try:
        params = { 'apikey': apikey, 'node': node, 'json': json.dumps({ name : value }) }
        resource = url + '/input/post.json?' + urllib.parse.urlencode(params)

        request = urllib.request.Request(resource)
        request.add_header('User-agent', srv.SCRIPTNAME)

        response = urllib.request.urlopen(request, timeout=timeout)
        data = response.read()
    except Exception as e:
        srv.logging.warn("Failed to send GET request to EmonCMS using %s: %s" % (resource, e))
        return False

    return True
