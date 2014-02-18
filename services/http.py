#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):
    ''' addrs: (method, url dict(params)) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    method = item.addrs[0]
    url    = item.addrs[1]
    params = item.addrs[2]

    # Try and transform the URL. Use original URL if it's not possible
    try:
        url = url.format(**item.data)
    except:
        pass

    for key in params.keys():
        try:
            params[key] = params[key].format(**item.data).encode('utf-8')
        except Exception, e:
            srv.logging.debug("Parameter %s cannot be formatted: %s" % (key, str(e)))
            return False

    message  = item.message

    if method.upper() == 'GET':
        try:
            resource = '%s/%s' % (url, urllib.urlencode(params))
            resp = urllib2.urlopen(resource)
            data = resp.read()
        except Exception, e:
            srv.logging.warn("Cannot GET %s: %s" % (resource, str(e)))
            return False

        return True

    if method.upper() == 'POST':
        try:
            encoded_params = urllib.urlencode(params)
            resp = urllib2.urlopen(url, encoded_params)
            data = resp.read()
            # print "POST returns ", data
        except Exception, e:
            srv.logging.warn("Cannot POST %s: %s" % (url, str(e)))
            return False

        return True

    srv.logging.warn("Unsupported HTTP method: %s" % (method))
    return False
