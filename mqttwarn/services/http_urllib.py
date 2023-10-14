#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

try:
    from urllib.parse import urlparse, urlencode, urljoin
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse  # type: ignore[no-redef]
    from urllib import urlencode, urljoin  # type: ignore[no-redef,attr-defined]
    from urllib2 import urlopen, Request, HTTPError  # type: ignore[no-redef]

import base64

try:
    import simplejson as json
except ImportError:
    import json  # type: ignore[no-redef]


def plugin(srv, item):
    """ addrs: (method, url, dict(params), list(username, password), json) """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    method = item.addrs[0]
    url    = item.addrs[1]
    params = item.addrs[2]
    timeout = item.config.get('timeout', 60)

    basicauth_token = None
    try:
        username, password = item.addrs[3]
        credentials = '%s:%s' % (username, password)
        basicauth_token = base64.b64encode(credentials.encode('utf-8')).decode()
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
                    srv.logging.exception("Parameter %s cannot be formatted" % key)
                    return False

    message  = item.message

    if method.upper() == 'GET':
        try:
            if params is not None:
                resource = url
                if not resource.endswith('?'):
                    resource = resource + '?'
                resource = resource + urlencode(params)
            else:
                resource = url

            request = Request(resource)

            if srv.SCRIPTNAME is not None:
                request.add_header('User-agent', srv.SCRIPTNAME)
            if basicauth_token is not None:
                request.add_header("Authorization", "Basic %s" % basicauth_token)

            resp = urlopen(request, timeout=timeout)
            data = resp.read()
            #srv.logging.debug("HTTP response:\n%s" % data)
        except Exception as e:
            srv.logging.warn("Cannot GET %s: %s" % (resource, e))
            return False

        return True

    if method.upper() == 'POST':
        try:
            request = Request(url)
            if params is not None:
                if tojson is not None:
                    encoded_params = json.dumps(params)
                    request.add_header('Content-Type', 'application/json')
                else:
                    encoded_params = urlencode(params)
            else:
                if tojson is not None:
                    encoded_params = item.payload
                    request.add_header('Content-Type', 'application/json')
                else:
                    encoded_params = message


            request.data = encoded_params.encode('utf-8')

            if srv.SCRIPTNAME is not None:
                request.add_header('User-agent', srv.SCRIPTNAME)
            if basicauth_token is not None:
                request.add_header("Authorization", "Basic %s" % basicauth_token)

            srv.logging.debug("before send")
            resp = urlopen(request, timeout=timeout)
            data = resp.read()
            #srv.logging.debug("HTTP response:\n%s" % data)
        except Exception as e:
            srv.logging.warn("Cannot POST %s: %s" % (url, e))
            return False

        return True

    srv.logging.warn("Unsupported HTTP method: %s" % (method))
    return False
