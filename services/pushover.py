#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The code for pushover() between cuts was written by Mike Matz and
# gracefully swiped from https://github.com/pix0r/pushover

import urllib
import urllib2
import urlparse
import json
import os

PUSHOVER_API = "https://api.pushover.net/1/"

class PushoverError(Exception): pass

def pushover(**kwargs):
    assert 'message' in kwargs

    if not 'token' in kwargs:
        kwargs['token'] = os.environ['PUSHOVER_TOKEN']
    if not 'user' in kwargs:
        kwargs['user'] = os.environ['PUSHOVER_USER']

    url = urlparse.urljoin(PUSHOVER_API, "messages.json")
    data = urllib.urlencode(kwargs)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    output = response.read()
    data = json.loads(output)

    if data['status'] != 1:
        raise PushoverError(output)

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def plugin(srv, item):

    message  = item.message
    addrs    = item.addrs
    title    = item.title
    priority = item.priority
    callback = item.callback

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # addrs is an array with two elements:
    # 0 is the user key
    # 1 is the app key

    try:
        userkey = addrs[0]
        appkey  = addrs[1]
    except:
        srv.logging.warn("No pushover userkey/appkey configured for target `%s'" % (item.target))
        return False

    params = {
            'retry' : 60,
            'expire' : 3600,
        }

    if title is not None:
        params['title'] = title

    if priority is not None:
        params['priority'] = priority

    if callback is not None:
        params['callback'] = callback

    try:
        srv.logging.debug("Sending pushover notification to %s [%s]..." % (item.target, params))
        pushover(message=message, user=userkey, token=appkey, **params)
        srv.logging.debug("Successfully sent pushover notification")
    except Exception, e:
        srv.logging.warn("Error sending pushover notification to %s [%s]: %s" % (item.target, params, str(e)))
        return False

    return True
