#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Mike McGinty <mach327()gmail.com>'
__copyright__   = 'Copyright 2015 Mike McGinty'
__license__ = """Eclipse Public License - v 1.0  (http://www.eclipse.org/legal/epl-v10.html)"""

import os
import sys
import time

import clr
from System.ComponentModel import Container
from System.Windows.Forms import NotifyIcon, MenuItem, ContextMenu
from System.Drawing import Icon
from System import EventHandler

# New icon every time. TTL seems to have very little effect.

class WinNotifyIcon:
    def __init__(self, location, tipicon, title, text, ttl):
        iconpath = os.path.dirname( location ) + "\\assets\\mqtt.ico"
        self.tip = NotifyIcon()
        self.tip.Text = "MQTTWarn (winnotify)"
        if os.path.exists( iconpath):
            self.tip.Icon = Icon( iconpath)
        else:
            from System.Drawing import SystemIcons
            self.tip.Icon = SystemIcons.Application
        self.tip.Visible = True
        self.tip.BalloonTipIcon = tipicon
        self.tip.BalloonTipTitle = title
        self.tip.BalloonTipText = text
        timeshown = time.time()
        self.expires = timeshown + (ttl/1000)
        self.tip.ShowBalloonTip(ttl)

    def remove(self):
        self.tip.Visible = False
        self.tip.Dispose()

def expired_icon(iconobj):
    if iconobj.expires < time.time():
        iconobj.remove()
        return True
    else:
        return False


def plugin(srv, item):
    """ (Very) Basic notification system that spawns an icon and associated balloontip in the notification area of the WIndows Desktop. Only tested with Windows 7.
    Requirements: pythonnet module """
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    location = os.path.dirname(os.path.abspath(__file__))
    enumicon = item.addrs[0] #Should be one of (None,Info,Warning,Error), controls the icon windows chooses for the balloontip (e.g. a white x in a red circle for "error")
    title = item.topic
    text  = item.message
    ttl = 0 #windows has its own ideas about icon/balloontip TTLs

    if len(plugin.icons) > 0:       #clean-up old icons
        plugin.icons[:] = [i for i in plugin.icons if expired_icon(i) ]

    try:
        plugin.icons.append( WinNotifyIcon(location, 0, title, text, ttl ) )
        return True

    except Exception, e:
        srv.logging.warning("Windows Basic Notification failure: %s" % (str(e)) )
        return False

plugin.icons = []
