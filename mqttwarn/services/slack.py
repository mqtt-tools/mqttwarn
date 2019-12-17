#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'


# 2018-11-13 - Update by psyciknz to add image upload function.  See Readme
#              Needs slacker 0.10.0 at a minimum

from slacker import Slacker


from builtins import str
import base64
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # check for service level token
    token = item.config.get('token')

    # get the target tokens
    addrs = list(item.addrs)
    as_user = False

    # check if we have the optional as_user token (extract and remove if so)
    if isinstance(addrs[-1], (bool)):
        as_user = addrs[-1]
        local_addrs = addrs[:len(addrs) - 1]

    # check for target level tokens (which have preference)
    try:
        if len(addrs) == 4:
            token, channel, username, icon = addrs
        else:
            channel, username, icon = addrs
    except Exception as e:
        srv.logging.error("Incorrect target configuration for target=%s: %s", item.target, e)
        return False

    # if no token then fail
    if token is None:
        srv.logging.error("No token found for slack")
        return False

    # if the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message
    # check if the message has been decoded from a JSON payload
    if 'message' in item.data:
        text = item.data['message']
    else:
        text = item.message

    # check if there is an image contained in a JSON payload
    # (support either an image URL or base64 encoded image)
    try:
        image = None
        if 'imageurl' in item.data:
            imageurl = item.data['imageurl']
            srv.logging.debug("Image url detected - %s" % imageurl)

            #Image payload has auth parms, so use the correct method for authenticating.
            if 'auth' in item.data:
                authtype = item.data['auth']
                authuser = item.data['user']
                authpass = item.data['password']
                if authtype == 'digest':
                    image = requests.get(imageurl, stream=True,auth=HTTPDigestAuth(authuser, authpass)).raw
                else:
                    image = requests.get(imageurl, stream=True,auth=HTTPBasicAuth(authuser, authpass)).raw
            else:
                image = requests.get(imageurl, stream=True).raw
            
        elif 'imagebase64' in item.data:
            imagebase64 = item.data['imagebase64']
            srv.logging.debug("Image (base64 encoded) detected")
            #image = base64.decodestring(imagebase64)
            image = base64.b64decode(str(imagebase64))
            filename = 'some_image.jpg'  
            #base 64 doesn't seem to decode properly.  So have to write it to a temp image, and reload it.
            #maybe this method might be dropped?
            with open(filename, 'wb') as f:
                f.write(image)
            
    except Exception as e:
        srv.logging.warning("Cannot download image: %s", e)

    try:
        slack = Slacker(token)
        if image is None:
            slack.chat.post_message(channel, text, as_user=as_user, username=username, icon_emoji=icon, unfurl_links=True)
        else:
            
            srv.logging.debug("Channel id: %s" % channel);
            channelname = channel.replace('#','')

            # weird check and re-read I had to do for base64 decoded images.
            if 'imagebase64' in item.data:
                with open(filename,'rb') as f2:
                    slack.files.upload(file_=f2,title=text,channels=slack.channels.get_channel_id(channelname))
            else:
                slack.files.upload(file_=image,title=text,channels=slack.channels.get_channel_id(channelname))
            srv.logging.debug("image posted")
    except Exception as e:
        srv.logging.warning("Cannot post to slack %s: %s" % (channel, e))
        return False

    return True

