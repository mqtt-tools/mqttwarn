#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from twilio.rest import TwilioRestClient


def plugin(srv, item):
    """ expects (accountSID, authToken, from, to) in addrs"""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

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
    except Exception as e:
        srv.logging.warn("Twilio failed: %s" % e)
        return False

    return True
