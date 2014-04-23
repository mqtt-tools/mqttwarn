#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Fabian Affolter <fabian()affolter-engineering.ch>'
__copyright__ = 'Copyright 2014 Fabian Affolter'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import xmpp     # pip install xmpp

def plugin(srv, item):
    """Send a message to XMPP recipient(s)."""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    xmpp_addresses = item.addrs
    sender = item.config['sender']
    password = item.config['password']
    text = item.message

    try:
        srv.logging.debug("Sending message to %s..." % (item.target))
        for target in xmpp_addresses:
            jid = xmpp.protocol.JID(sender)
            connection = xmpp.Client(jid.getDomain(),debug=[])
            connection.connect()
            connection.auth(jid.getNode(), password, resource=jid.getResource())
            connection.send(xmpp.protocol.Message(target, text))
        srv.logging.debug("Successfully sent message")
    except Exception, e:
        srv.logging.error("Error sending message to %s: %s" % (item.target, str(e)))
        return False

    return True
