#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_SLACK=True
try:
    from slacker import Slacker
except ImportError:
    HAVE_SLACK=False

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    if HAVE_SLACK == False:
        srv.logging.error("slacker module missing")
        return False

    # check for service level token
    token = item.config.get('token')

    # check for target level tokens (which have preference)
    try:
        if len(item.addrs) == 5:
            token, channel, username, icon, as_user = ( item.addrs + [False] )[:5]
        else:
            channel, username, icon, as_user = ( item.addrs + [False] )[:4]
    except:
        srv.logging.error("Incorrect target configuration for target=%s: %s", item.target, str(e))
        return False

    # if no token then fail
    if token is None:
        srv.logging.error("No token found for slack")
        return False

    # if the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    try:
        slack = Slacker(token)
        slack.chat.post_message(channel, text, as_user=as_user, username=username, icon_emoji=icon)
    except Exception, e:
        srv.logging.warning("Cannot post to slack %s: %s" % (channel, str(e)))
        return False

    return True
