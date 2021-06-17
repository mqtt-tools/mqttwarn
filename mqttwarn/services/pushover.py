#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014-2019 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

# The code for pushover() between cuts was written by Mike Matz and
# gracefully swiped from https://github.com/pix0r/pushover
#
# 2019-12-17 - Update by jpmens to remove urlparse
# 2018-11-13 - Update by psyciknz to add image service authentication options (digest/basic)
# 2018-04-07 - Updated by psyciknz to add the image upload function
#              as supported by pushover
#            - changed from urllib2 to requests for the loading of images
#              from a json payload via the "imageurl" attribute or by decoding
#              a base64 encoded image in the the "image" attribute.
#            - text to accompany the image comes from the "message" attribute
#              of the json payload.

import os
import base64
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests.compat import urljoin

PUSHOVER_API = "https://api.pushover.net/1/"


class PushoverError(Exception): pass


def pushover(image, **kwargs):
    assert 'message' in kwargs

    url = urljoin(PUSHOVER_API, "messages.json")
    headers = { 'User-Agent': 'mqttwarn' }

    if image:
        attachment = { "attachment": ( "image.jpg", image, "image/jpeg" )}
        r = requests.post(url, data=kwargs, files=attachment, headers=headers)
    else:
        r = requests.post(url, data=kwargs, headers=headers)

    if r.json()['status'] != 1:
        raise PushoverError(r.content)


def plugin(srv, item):

    addrs    = item.addrs
    title    = item.title
    priority = item.priority

    # optional callback URL
    callback = item.config.get('callback', None)

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # addrs is an array with two or three elements:
    # 0 is the user key
    # 1 is the app key
    # 2 (if present) is the PushOver sound to play for the message

    try:
        userkey = addrs[0]
        token   = addrs[1]
    except:
        srv.logging.warning("Invalid address configuration for target `%s'" % (item.target))
        return False

    if userkey is None and "PUSHOVER_USER" in os.environ:
        userkey = os.environ["PUSHOVER_USER"].strip()
    if token is None and "PUSHOVER_TOKEN" in os.environ:
        token = os.environ["PUSHOVER_TOKEN"].strip()

    if not userkey or not token:
        srv.logging.warning("No pushover credentials configured for target `%s'" % (item.target))
        return False

    params = {
            'retry'  : 60,
            'expire' : 3600,
        }

    if len(addrs) > 2 and addrs[2]:
        params['sound'] = addrs[2]

    if len(addrs) > 3:
        params['devices'] = addrs[3]

    if title is not None:
        params['title'] = title

    if priority is not None:
        params['priority'] = priority

    if callback is not None:
        params['callback'] = callback

    # check if the message has been decoded from a JSON payload
    if 'message' in item.data:
        params['message'] = item.data['message']
    else:
        params['message'] = item.message

    # check if there is an image contained in a JSON payload
    # (support either an image URL or base64 encoded image)
    image = None
    if 'imageurl' in item.data:
        imageurl = item.data['imageurl']
        srv.logging.debug("Image url detected - %s" % imageurl)
        if 'auth' in item.data:
            authtype = item.data['auth']
            authuser = item.data['user']
            authpass = item.data['password']
            if authtype == 'digest':
                image = requests.get(imageurl, stream=True, auth=HTTPDigestAuth(authuser, authpass)).raw
            else:
                image = requests.get(imageurl, stream=True, auth=HTTPBasicAuth(authuser, authpass)).raw
        else:
            image = requests.get(imageurl, stream=True).raw
    elif 'imagebase64' in item.data:
        imagebase64 = item.data['imagebase64']
        srv.logging.debug("Image (base64 encoded) detected")
        image = base64.decodebytes(imagebase64)

    try:
        srv.logging.debug("Sending pushover notification to %s [%s]...." % (item.target, params))
        pushover(image=image, user=userkey, token=token, **params)
        srv.logging.debug("Successfully sent pushover notification")
    except Exception as e:
        srv.logging.warning("Error sending pushover notification: %s" % e)
        return False

    return True
