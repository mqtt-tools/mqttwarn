#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_TWILIO=True
try:
    from twilio.rest import TwilioRestClient
except ImportError:
    HAVE_TWILIO=False


def plugin(srv, item):
    ''' expects (accountSID, authToken, from, to) in addrs'''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)
    if not HAVE_TWILIO:
        srv.logging.warn("twilio-python is not installed")
        return False

    try:
        account_sid, auth_token, from_nr, to_nr = item.addrs
    except:
        srv.logging.warn("Twilio target is incorrectly configured")
        return False

    text = item.message

    try:
        client = TwilioRestClient(account_sid, auth_token)
        message = client.messages.create(
                    body=text,
                    to=to_nr,
                    from_=from_nr)
        srv.logging.debug("Twilio returns %s" % (message.sid))
    except Exception, e:
        srv.logging.warn("Twilio failed: %s" % (str(e)))
        return False

    return True
