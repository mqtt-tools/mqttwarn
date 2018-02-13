#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
__author__    = 'Bram Hendrickx'
__copyright__ = 'Copyright 2016 Bram Hendrickx'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

Original script by Bram Hendrickx. https://github.com/jpmens/mqttwarn/blob/master/services/ifttt.py
Modified to work with the autoremote api https://joaoapps.com/autoremote/

'''
__author__    = 'Michael Brougham'
__copyright__ = 'Copyright 2018 Michael Brougham'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""


#import json
import requests

def plugin(srv, item):
    ''' expects (apikey, password, target, group, ttl) in addrs '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        srv.logging.debug("Sending to autoremote service")
        url = "https://" + item.addrs[0] + ":" + item.addrs[1]
        requests.get('https://autoremotejoaomgcd.appspot.com/sendmessage?key=' + item.addrs[0] + '&message=' + item.message + '&target=' + item.addrs[2] + '&sender=' + item.topic + '&password=' + item.addrs[1] + '&ttl=' + item.addrs[4] + '&collapseKey=' + item.addrs[3])
	srv.logging.debug("Successfully sent to autoremote service")
    except Exception, e:
        srv.logging.warning("Failed to send message to autoremote service" % (str(e)))
        return False

    return True
