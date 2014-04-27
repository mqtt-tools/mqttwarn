#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

from xmlrpclib import ServerProxy
import urllib

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    host     = item.config['host']
    port     = item.config['port']
    username = item.config['username']
    password = item.config['password']
 
    gateway  = item.addrs[0]
    number   = item.addrs[1]    
    title    = item.title
    message  = item.message

    try:
        # Google Translate API
        params = urllib.urlencode({ 'tl' : 'en', 'q' : message })
        shout_url = "shout://translate.google.com/translate_tts?" + params
        # Freeswitch API
        server = ServerProxy("http://%s:%s@%s:%d" % (username, password, host, port))
        # channel variables we need to setup the call
        channel_vars = "{ignore_early_media=true,originate_timeout=60,origination_caller_id_name='" + title + "'}"
        # originate the call
        server.freeswitch.api("originate", channel_vars + gateway + number + " &playback(" + shout_url + ")")
    except Exception, e:
        srv.logging.error("Error sending XBMC notification to %s [%s]: %s" % (item.target, xbmchost, str(e)))
        return False

    return True
