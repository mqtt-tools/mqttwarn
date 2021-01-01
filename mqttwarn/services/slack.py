#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

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
            image = base64.b64decode(str(imagebase64))
            
    except Exception as e:
        srv.logging.warning("Cannot download image: %s", e)

    try:
        slack = WebClient(token=token)
        if image is None:
            slack.chat_postMessage(channel=channel, text=text, username=username, icon_emoji=icon, unfurl_links=True)
        else:
            
            srv.logging.debug("Channel id: %s" % channel);

            slack.files_upload(file=image,title=text,channels=channel)
            srv.logging.debug("image posted")
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        srv.logging.warning("Cannot post to slack %s: %s" % (channel, e.response['error']))
        return False
    except Exception as e:
        srv.logging.warning("Cannot post to slack %s: %s" % (channel, e))
        return False

    return True

