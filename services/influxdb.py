#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2016 Ben Jones'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import requests
import logging

# disable info logging in requests module (e.g. connection pool message for every post request)
logging.getLogger("requests").setLevel(logging.WARNING)

def plugin(srv, item):
    ''' addrs: (measurement) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    host        = item.config['host']
    port        = item.config['port']
    username    = item.config['username']
    password    = item.config['password']
    database    = item.config['database']

    measurement = item.addrs[0]
    tag         = "topic=" + item.topic.replace('/', '_')
    value       = item.payload
    
    try:
        url = "http://%s:%d/write?db=%s" % (host, port, database)
        data = measurement + ',' + tag + ' value=' + value
        
        if username is None:
            r = requests.post(url, data=data)
        elif:
            r = requests.post(url, data=data, auth=(username, password))
        
        # success
        if r.status_code == 204:
            return True
            
        # request accepted but couldn't be completed (200) or failed (otherwise)
        if r.status_code == 200:
            srv.logging.warn("POST request could not be completed: %s" % (r.text))
        else:
            srv.logging.warn("POST request failed: (%s) %s" % (r.status_code, r.text))
        
    except Exception, e:
        srv.logging.warn("Failed to send POST request to InfluxDB server using %s: %s" % (url, str(e)))

    return False
