#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Przemek Anuszek <przemas75()gmail.com>'
__copyright__ = 'Copyright 2016 Przemek Anuszek'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from fbchat import Client
from fbchat.models import *


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    client = item.addrs[0]
    password = item.addrs[1]
    friend = item.addrs[2]

    fbclient = Client(client, password)
    friends = fbclient.searchForUsers(friend)
    ffriend = friends[0]

    srv.logging.debug("user %s" % (item.target))

    text = item.message
    try:
        srv.logging.debug("Sending msg to %s..." % (item.target))
        sent = fbclient.sendMessage(text, thread_id=ffriend.uid, thread_type=ThreadType.USER)
        srv.logging.debug("Successfully sent message")
    except Exception as e:
        srv.logging.error("Error sending fbchat to %s: %s" % (item.target, e))
        return False
    client.logout()
    return True
