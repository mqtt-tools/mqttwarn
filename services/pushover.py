#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The code for pushover() between cuts was written by Mike Matz and
# gracefully swiped from https://github.com/pix0r/pushover
#
# 2018-04-07 - Updated by psyciknz to add the image upload function
#              as supported by pushover
#            - changed from urllib2 to requests for the loading of images
#              from a json payload via the "imageurl" attribute or by decoding
#              a base64 encoded image in the the "image" attribute.
#            - text to accompany the image comes from the "message" attribute
#              of the json payload.

import base64
import requests
import urlparse
import json
import os

PUSHOVER_API = "https://api.pushover.net/1/"

class PushoverError(Exception): pass

def pushover(message, user, token, params, filepayload=None):

    if token is None:
        params['token'] = os.environ['PUSHOVER_TOKEN']
    else:
        params['token'] = token
    #params['token'] = token

    #if user is None:
    #    params=['user'] = os.environ['PUSHOVER_USER']
    #else:
    #    params['user'] = user
    params["user"] = user

    params["message"] = message

    url = urlparse.urljoin(PUSHOVER_API, "messages.json")

    if filepayload is None:
        r = requests.post(url,data=params, headers={'User-Agent': 'Python'})
    else:
        r = requests.post(url,data=params, files=filepayload, headers={'User-Agent': 'Python'})
    output = r.text
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

    # optional callback URL
    callback = item.config.get('callback', None)

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # addrs is an array with two or three elements:
    # 0 is the user key
    # 1 is the app key
    # 2 (if present) is the PushOver sound to play for the message

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

    if len(addrs) > 2:
        params['sound'] = addrs[2]

    if title is not None:
        params['title'] = title

    if priority is not None:
        params['priority'] = priority

    if callback is not None:
        params['callback'] = callback

    srv.logging.debug("=================Starting Image processing")

    filepayload=None
    try:
        srv.logging.debug("Loading mesasgejson")

        messagejson = json.loads(message)
        srv.logging.debug("Mesasgejson loaded, looking for imageurl")

        if 'imageurl' in messagejson:
            srv.logging.debug("Image url is in json object %s" % messagejson["imageurl"])
            filepayload = { "attachment": ("image.jpg",requests.get(messagejson["imageurl"], stream=True).raw, "image/jpeg") }
            message = messagejson["message"]
        elif 'image' in messagejson:
            srv.logging.debug("Image is in json object %s" % messagejson["image"])
            filepayload = { "attachment": ("image.jpg",base64.decodestring(messagejson["image"]), "image/jpeg") }
            message = messagejson["message"]
        else:
            srv.logging.debug("No image could be found")



    except Exception, e:
        srv.logging.warn("Error sending pushover notification to %s [%s]: %s" % (item.target, params, str(e)))
        pass


    try:
        srv.logging.debug("Sending pushover notification to %s [%s]..." % (item.target, params))
        srv.logging.debug("Sending pushover notification to %s [%s]..." % (item.target, message))
        pushover(message, userkey, appkey,params,filepayload=filepayload)
        srv.logging.debug("Successfully sent pushover notification")
    except Exception, e:
        srv.logging.warn("Error sending pushover notification to %s [%s]: %s" % (item.target, params, str(e)))
        return False

    return True
