#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_PUSHBULLET=True
try:
    from pushbullet.pushbullet import PushBullet
except ImportError:
    try:
        from pushbullet import PushBullet
    except ImportError:
        HAVE_PUSHBULLET=False

def plugin(srv, item):
    ''' expects (apikey, device_id) in adddrs '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)
    if not HAVE_PUSHBULLET:
        srv.logging.warn("pushbullet is not installed")
        return False

	recipient_type = "device_iden"
    try:
        apikey, device_id = item.addrs
    except:
		try:
			apikey, device_id, recipient_type = item.addrs
		except:
			srv.logging.warn("pushbullet target is incorrectly configured")
			return False

    text = item.message
    title = item.get('title', srv.SCRIPTNAME)

    try:
        srv.logging.debug("Sending pushbullet notification to %s..." % (item.target))
        pb = PushBullet(apikey)
        pb.pushNote(device_id, title, text, recipient_type)
        srv.logging.debug("Successfully sent pushbullet notification")
    except Exception, e:
        srv.logging.warning("Cannot notify pushbullet: %s" % (str(e)))
        return False

    return True
