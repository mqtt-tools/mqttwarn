#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__	= 'Mike McGinty <mach327()gmail.com>'
__copyright__	= 'Copyright 2015 Mike McGinty'
__license__	= """Eclipse Public License - v 1.0  (http://www.eclipse.org/legal/epl-v10.html)"""

import os
import sys
import subprocess

def plugin(srv, item):
	""" (Very) Basic notification system that spawns an icon and associated balloontip in the notification area of the WIndows Desktop. Only tested with Windows 7.
	Requires powershell (natch), an execution policy that lets the script run, and obviously all the mqttwarn requirements installed. """
	srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

	location = os.path.dirname(os.path.abspath(__file__))
	psscript = os.path.splitext( os.path.abspath(__file__) )[0] + ".ps1"
	enumicon = item.addrs[0] #Should be one of (None,Info,Warning,Error), controls the icon windows chooses for the balloontip (e.g. a white x in a red circle for "error")
	title = item.topic
	text  = item.message
	try:
		p = subprocess.Popen( ["powershell.exe",
			psscript, 
			"-TrayIcon", os.path.dirname(location) + "\\assets\\mqtt.ico",
			"-BalloonIcon", "'" + enumicon + "'",
			"-BalloonTitle","'" + title + "'",
			"-BalloonBody", "'" + text + "'",
			], stdout=sys.stdout)
		p.communicate()
		return True
	except Exception, e:
		srv.logging.warning("Windows Basic Notification failure: %s" % (str(e)) )
		return False
