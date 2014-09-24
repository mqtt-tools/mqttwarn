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

    token = item.config.get('token')
    if token is None:
        srv.logging.error("No token found for slack")
        return False

    try:
        channel, username, icon = item.addrs
    except:
        srv.logging.error("Incorrect target configuration")
        return False

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    try:
        slack = Slacker(token)
        slack.chat.post_message(channel, text, username=username, icon_emoji=icon)
    except Exception, e:
        srv.logging.warning("Cannot post to slack `%s': %s" % (filename, str(e)))
        return False

    return True
