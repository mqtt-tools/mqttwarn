#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Ben Jones'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()

from xmlrpc.client import ServerProxy
import urllib.request, urllib.parse, urllib.error


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    host      = item.config['host']
    port      = item.config['port']
    username  = item.config['username']
    password  = item.config['password']
    ttsurl    = item.config['ttsurl']
    ttsparams = item.config['ttsparams']
 
    gateway   = item.addrs[0]
    number    = item.addrs[1]    
    title     = item.title

    if ttsurl.startswith('http://'):
        ttsurl = ttsurl[7:]
    elif ttsurl.startswith('https://'):
        ttsurl = ttsurl[8:]

    if ttsparams is not None:
        for key in list(ttsparams.keys()):

            # { 'q' : '@message' }
            # Quoted field, starts with '@'. Do not use .format, instead grab
            # the item's [message] and inject as parameter value.
            if ttsparams[key].startswith('@'):         # "@message"
                ttsparams[key] = item.get(ttsparams[key][1:], "NOP")

            else:
                try:
                    ttsparams[key] = ttsparams[key].format(**item.data).encode('utf-8')
                except Exception as e:
                    srv.logging.debug("Parameter %s cannot be formatted: %s" % (key, e))
                    return False

    try:
        # TTS service
        shout_url = "shout://%s" % ttsurl
        if ttsparams is not None:
            if not shout_url.endswith('?'):
                shout_url = shout_url + '?'
            shout_url = shout_url + urllib.parse.urlencode(ttsparams)
        # debugging
        srv.logging.debug("Shout URL: %s" % shout_url)
        # Freeswitch API
        server = ServerProxy("http://%s:%s@%s:%d" % (username, password, host, port))
        # channel variables we need to setup the call
        channel_vars = "{ignore_early_media=true,originate_timeout=60,origination_caller_id_name='" + title + "'}"
        # originate the call
        server.freeswitch.api("originate", channel_vars + gateway + number + " &playback(" + shout_url + ")")
    except Exception as e:
        srv.logging.error("Error originating Freeswitch VOIP call to %s via %s%s: %s" % (item.target, gateway, number, e))
        return False

    return True
