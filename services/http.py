#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
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
    ''' addrs: (method, url dict(params), list(username, password)) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    method = item.addrs[0]
    url    = item.addrs[1]
    params = item.addrs[2]
    auth   = item.addrs[3]
    timeout = item.config.get('timeout', 60)

    # Try and transform the URL. Use original URL if it's not possible
    try:
        url = url.format(**item.data)
    except:
        pass

    if params is not None:
        for key in params.keys():
            try:
                params[key] = params[key].format(**item.data).encode('utf-8')
            except Exception, e:
                srv.logging.debug("Parameter %s cannot be formatted: %s" % (key, str(e)))
                return False

    message  = item.message

    if method.upper() == 'GET':
        try:
            if params is not None:
                resource = url
                if not resource.endswith('?'):
                    resource = resource + '?'
                resource = resource + urllib.urlencode(params)
            else:
                resource = url

            request = urllib2.Request(resource)
            request.add_header('User-agent', srv.SCRIPTNAME)

            if auth is not None:
                base64string = base64.encodestring('%s:%s' % (auth[0], auth[1])).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % base64string)

            resp = urllib2.urlopen(request, timeout=timeout)
            data = resp.read()
        except Exception, e:
            srv.logging.warn("Cannot GET %s: %s" % (resource, str(e)))
            return False

        return True

    if method.upper() == 'POST':
        try:
            request = urllib2.Request(url)
            if params is not None:
                encoded_params = urllib.urlencode(params)
            else:
                encoded_params = message

            request.add_data(encoded_params)
            request.add_header('User-agent', srv.SCRIPTNAME)
            if auth is not None:
                base64string = base64.encodestring('%s:%s' % (auth[0], auth[1])).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % base64string)
            resp = urllib2.urlopen(request, timeout=timeout)
            data = resp.read()
            # print "POST returns ", data
        except Exception, e:
            srv.logging.warn("Cannot POST %s: %s" % (url, str(e)))
            return False

        return True

    srv.logging.warn("Unsupported HTTP method: %s" % (method))
    return False
