#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Fabian Affolter <fabian()affolter-engineering.ch>'
__copyright__ = 'Copyright 2014 Fabian Affolter'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from gi.repository import Notify


def plugin(srv, item):
    """Send a message to the user's desktop notification system."""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__,
            item.service, item.target)

    title = item.addrs[0]
    text = item.message

    try:
        srv.logging.debug("Sending notification to the user's desktop")
        Notify.init('mqttwarn')
        n = Notify.Notification.new(
            title,
            text,
            '/usr/share/icons/gnome/32x32/places/network-server.png')
        n.show()
        srv.logging.debug("Successfully sent notification")
    except Exception as e:
        srv.logging.warning("Cannot invoke notification to linux: %s" % e)
        return False

    return True
