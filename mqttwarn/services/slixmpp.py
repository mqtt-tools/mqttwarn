#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on xmpp plugin
__originalauthor__ = 'Fabian Affolter <fabian()affolter-engineering.ch>'
__author__         = 'Remi Vincent <remi.vincent()gmail.com>'
__copyright__      = 'Copyright 2020 Remi Vincent'
__license__        = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import slixmpp
import asyncio

class send_msg_bot(slixmpp.ClientXMPP):
    def __init__(self, sender, password, recipient, message, loop):
        self.loop = loop
        asyncio.set_event_loop(loop)
        slixmpp.ClientXMPP.__init__(self, sender, password)
        self.recipient = recipient
        self.message = message
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_message(mto = self.recipient, mbody = self.message, mtype = 'chat')
        self.disconnect()

def plugin(srv, item):
    """Send a message to XMPP recipient(s)."""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    xmpp_addresses = item.addrs
    sender = item.config['sender']
    password = item.config['password']
    text = item.message

    if not xmpp_addresses:
        srv.logging.warn("Skipped sending XMPP notification to %s, "
                         "no addresses configured" % (item.target))
        return False

    try:
        srv.logging.debug("Sending XMPP notification to %s, addresses: %s" % (item.target, xmpp_addresses))
        loop = asyncio.new_event_loop()
        for target in xmpp_addresses:
            xmpp = send_msg_bot(sender, password, target, text, loop)
            xmpp.connect()
            xmpp.process(forever=False)
        srv.logging.debug("Successfully sent message")
    except Exception as e:
        srv.logging.error("Error sending message to %s: %s" % (item.target, e))
        return False

    return True
