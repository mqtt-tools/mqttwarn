#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Fabian Affolter <fabian()affolter-engineering.ch>'
__copyright__ = 'Copyright 2014 Fabian Affolter'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_PASTEBIN=True
try:
    from pastebin import PastebinAPI
except:
    HAVE_PASTEBIN=False

def plugin(srv, item):
    """ Pushlish the message to pastebin.com """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__,
        item.service, item.target)

    if HAVE_PASTEBIN is False:
        srv.logging.warn("Pastebin module is not available.")
        return False

    pastebin_data = item.addrs

    pastebinapi = PastebinAPI()
    api_dev_key = pastebin_data[0]
    username = pastebin_data[1]
    password = pastebin_data[2]
    pastename = 'mqttwarn'
    pasteprivate = pastebin_data[3]
    expiredate = pastebin_data[4]

    text = item.message

    try:
        api_user_key = pastebinapi.generate_user_key(
            api_dev_key,
            username,
            password)
    except Exception, e:
        srv.logging.warn("Cannot retrieve session data from pastebin: %s" % (str(e)))
        return False

    try:
        srv.logging.debug("Adding entry to pastebin.com as user %s..." % (username))
        pastebinapi.paste(
            api_dev_key,
            text,
            api_user_key = api_user_key,
            paste_name = pastename,
            paste_format = None,
            paste_private = pasteprivate,
            paste_expire_date = expiredate
            )
        srv.logging.debug("Successfully added paste to pastebin")
    except Exception, e:
        srv.logging.warn("Cannot publish to pastebin: %s" % (str(e)))
        return False

    return True
