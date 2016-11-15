#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import fbchat


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    client = item.addrs[0]
    password = item.addrs[1]
    friend = item.addrs[2]

    fbclient = fbchat.Client(client, password)
    friends = fbclient.getUsers(friend)
    ffriend = friends[0]
    srv.logging.debug("user %s" % (item.target))

    text = item.message
    try:
        srv.logging.debug("Sending msg to %s..." % (item.target))
        sent = fbclient.send(ffriend.uid, text)
        srv.logging.debug("Successfully sent message")
    except Exception, e:
        srv.logging.error("Error sending fbchat to %s: %s" % (item.target, str(e)))
        return False

    return True
