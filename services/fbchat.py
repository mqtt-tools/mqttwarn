#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Przemek Anuszek <przemas75()gmail.com>'
__copyright__ = 'Copyright 2016 Przemyslaw Anuszek'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import fbchat


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

#    client = fbchat.Client("YOUR_ID", "YOUR_PASSWORD")
    fbchat_keys = item.addrs

    fbclient = fbchat.Client(
        username        = fbchat_keys[0],
        password        = fbchat_keys[1]
    )
    fbfriend = fbclient.getUsers(
        friend          = fbchat_keys[2]
    )
    #friends = client.getUsers("FRIEND'S NAME")  # return a list of names
    #friend = friends[0]

    text = item.message[0:138]
    try:
        srv.logging.debug("Sending msg to %s..." % (item.target))
        sent = fbclient.send(fbfriend, text)
        srv.logging.debug("Successfully sent tweet")
#    except twitter.TwitterError, e:
#        srv.logging.error("FbChatError: %s" % (str(e)))
#        return False
    except Exception, e:
        srv.logging.error("Error sending tweet to %s: %s" % (item.target, str(e)))
        return False

    return True
