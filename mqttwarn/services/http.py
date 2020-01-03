#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()

import urllib.request, urllib.parse, urllib.error
import base64

try:
    import simplejson as json
except ImportError:
    import json


def plugin(srv, item):
    """ addrs: (method, url, dict(params), list(username, password), json) """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    method = item.addrs[0]
    url    = item.addrs[1]
    params = item.addrs[2]
    timeout = item.config.get('timeout', 60)

    auth = None
    try:
        username, password = item.addrs[3]
        auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    except:
        pass

    tojson = None
    try:
        tojson = item.addrs[4]
    except:
        pass

    # Try and transform the URL. Use original URL if it's not possible
    try:
        url = url.format(**item.data)
    except:
        pass

    if params is not None:
        for key in list(params.keys()):

            # { 'q' : '@message' }
            # Quoted field, starts with '@'. Do not use .format, instead grab
            # the item's [message] and inject as parameter value.
            if params[key].startswith('@'):         # "@message"
                params[key] = item.get(params[key][1:], "NOP")

            else:
                try:
                    params[key] = params[key].format(**item.data).encode('utf-8')
                except Exception as e:
                    srv.logging.debug("Parameter %s cannot be formatted: %s" % (key, e))
                    return False

    message  = item.message

    if method.upper() == 'GET':
        try:
            if params is not None:
                resource = url
                if not resource.endswith('?'):
                    resource = resource + '?'
                resource = resource + urllib.parse.urlencode(params)
            else:
                resource = url

            request = urllib.request.Request(resource)
            request.add_header('User-agent', srv.SCRIPTNAME)

            if auth is not None:
                request.add_header("Authorization", "Basic %s" % auth)

            resp = urllib.request.urlopen(request, timeout=timeout)
            data = resp.read()
        except Exception as e:
            srv.logging.warn("Cannot GET %s: %s" % (resource, e))
            return False

        return True

    if method.upper() == 'POST':
        try:
            request = urllib.request.Request(url)
            if params is not None:
                if tojson is not None:
                    encoded_params = json.dumps(params)
                    request.add_header('Content-Type', 'application/json')
                else:
                    encoded_params = urllib.parse.urlencode(params)
            else:
                encoded_params = message

            request.add_data(encoded_params)
            request.add_header('User-agent', srv.SCRIPTNAME)
            if auth is not None:
                request.add_header("Authorization", "Basic %s" % auth)
            resp = urllib.request.urlopen(request, timeout=timeout)
            data = resp.read()
            # print "POST returns ", data
        except Exception as e:
            srv.logging.warn("Cannot POST %s: %s" % (url, e))
            return False

        return True

    srv.logging.warn("Unsupported HTTP method: %s" % (method))
    return False
