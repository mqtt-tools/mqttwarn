#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import urlparse
import json
import os

PUSHSAFER_API = "https://www.pushsafer.com/"

class PushsaferError(Exception): pass

def pushsafer(**kwargs):
    assert 'message' in kwargs

    if not 'privatekey' in kwargs:
        kwargs['privatekey'] = os.environ['PUSHSAFER_TOKEN']

    url = urlparse.urljoin(PUSHSAFER_API, "api")
    data = urllib.urlencode(kwargs)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req, timeout=3)
    output = response.read()
    data = json.loads(output)

    if data['status'] != 1:
        raise PushsaferError(output)

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

def plugin(srv, item):

    message  = item.message
    addrs    = item.addrs
    title    = item.title


    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)
    
    # based on the Pushsafer API (https://www.pushsafer.com/en/pushapi)
    # addrs is an array with two or three elements:
    # 0 is the private or alias key
    # 1 (if present) is the Pushsafer device or device group id where the message is to be sent
    # 2 (if present) is the Pushsafer icon to display in the message
    # 3 (if present) is the Pushsafer sound to play for the message
    # 4 (if present) is the Pushsafer vibration for the message
    # 5 (if present) is the Pushsafer URL or URL Scheme
    # 6 (if present) is the Pushsafer Title of URL
    # 7 (if present) is the Pushsafer Time in minutes, after which message automatically gets purged
    # 8 (if present) is the Pushsafer priority, integer -2, -1, 0, 1, 2
    # 9 (if present) is the Pushsafer retry after which time (in secomds 60-10800) a message should resend
    # 10 (if present) is the Pushsafer expire after which time (in secomds 60-10800) the retry should stopped
    # 11 (if present) is the Pushsafer answer, 1 = Answer, 0 = no possibilty to answer

    try:
        appkey  = addrs[0]
    except:
        srv.logging.warn("No pushsafer private or alias key configured for target `%s'" % (item.target))
        return False

    params = {
            'expire' : 3600,
        }

    if len(addrs) > 1:
        params['d'] = addrs[1]

    if len(addrs) > 2:
        params['i'] = addrs[2]

    if len(addrs) > 3:
        params['s'] = addrs[3]

    if len(addrs) > 3:
        params['v'] = addrs[4]

    if len(addrs) > 4:
        params['u'] = addrs[5]

    if len(addrs) > 5:
        params['ut'] = addrs[6]

    if len(addrs) > 6:
        params['l'] = addrs[7]

    if len(addrs) > 7:
        params['l'] = addrs[8]

    if len(addrs) > 8:
        params['pr'] = addrs[9]

    if len(addrs) > 9:
        params['re'] = addrs[10]

    if len(addrs) > 10:
        params['ex'] = addrs[11]
        
    if title is not None:
        params['a'] = title

    try:
        srv.logging.debug("Sending pushsafer notification to %s [%s]..." % (item.target, params))
        pushsafer(m=message, k=appkey, **params)
        srv.logging.debug("Successfully sent pushsafer notification")
    except Exception, e:
        srv.logging.warn("Error sending pushsafer notification to %s [%s]: %s" % (item.target, params, str(e)))
        return False

    return True
