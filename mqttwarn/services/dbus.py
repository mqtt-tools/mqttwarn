#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Fabian Affolter <fabian()affolter-engineering.ch>'
__copyright__ = 'Copyright 2014 Fabian Affolter'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import dbus


def plugin(srv, item):
    """Send a message through dbus to the user's desktop."""

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    text = item.message
    summary = item.addrs[0]
    app_name = item.get('title', srv.SCRIPTNAME)
    replaces_id = 0
    service = 'org.freedesktop.Notifications'
    path = '/' + service.replace('.', '/')
    interface = service
    app_icon = '/usr/share/icons/gnome/32x32/places/network-server.png'
    expire_timeout = 1000
    actions = []
    hints = []

    try:
        srv.logging.debug("Sending message to %s..." % (item.target))
        session_bus = dbus.SessionBus()
        obj = session_bus.get_object(service, path)
        interface = dbus.Interface(obj, interface)
        interface.Notify(app_name, replaces_id, app_icon, summary, text,
                    actions, hints, expire_timeout)
        srv.logging.debug("Successfully sent message")
    except Exception as e:
        srv.logging.error("Error sending message to %s: %s" % (item.target, e))
        return False

    return True
