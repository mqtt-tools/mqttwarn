#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Fabian Affolter <fabian()affolter-engineering.ch>'
__copyright__ = 'Copyright 2014 Fabian Affolter'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import xmpp


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
        for target in xmpp_addresses:
            jid = xmpp.protocol.JID(sender)
            connection = xmpp.Client(jid.getDomain(),debug=[])
            connection.connect()
            connection.auth(jid.getNode(), password, resource=jid.getResource())
            connection.send(xmpp.protocol.Message(target, text))
        srv.logging.debug("Successfully sent message")
    except Exception as e:
        srv.logging.error("Error sending message to %s: %s" % (item.target, e))
        return False

    return True


def xmpppy_monkeypatch_ssl():
    """
    Mitigate "AttributeError: '_ssl._SSLSocket' object has no attribute 'issuer'"

    Monkey-patched _startSSL method from
    https://raw.githubusercontent.com/freebsd/freebsd-ports/master/net-im/py-xmpppy/files/patch-xmpp-transports.py
    """
    import ssl

    def _startSSL(self):
        """ Immidiatedly switch socket to TLS mode. Used internally."""
        """ Here we should switch pending_data to hint mode."""
        tcpsock=self._owner.Connection
        tcpsock._sslObj    = ssl.wrap_socket(tcpsock._sock, None, None)
        tcpsock._sslIssuer = tcpsock._sslObj.getpeercert().get('issuer')
        tcpsock._sslServer = tcpsock._sslObj.getpeercert().get('server')
        tcpsock._recv = tcpsock._sslObj.read
        tcpsock._send = tcpsock._sslObj.write

        tcpsock._seen_data=1
        self._tcpsock=tcpsock
        tcpsock.pending_data=self.pending_data
        tcpsock._sock.setblocking(0)

        self.starttls='success'

    from xmpp.transports import TLS
    TLS._startSSL = _startSSL
