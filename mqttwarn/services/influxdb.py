#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2016 Ben Jones'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

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
    value       = item.message

    # retention policy - "&rp=" is valid in the url, so default=''
    rp          = item.config.get('rp', '')
    # precision=[ns,u,ms,s,m,h] - optional, default=nanosecond
    precision   = item.config.get('precision', 'ns')

    # allow overrides per target
    # 'target'  = [ 'measurement', 'database',    'rp', 'precision' ]
    if (len(item.addrs) > 1):
        database = item.addrs[1] or database
        if (len(item.addrs) > 2):
            rp = item.addrs[2] or rp
            if (len(item.addrs) > 3):
                precision = item.addrs[3] or precision

    try:
        url = "http://%s:%d/write?db=%s&rp=%s&precision=%s" % (host, port, database, rp, precision)

        # influxdb line protocol:
        # measurement,tagKey1=tagVal1,tagKey2=tagVal2 field1=value1,field2=value2 Timestamp
        # sample format in .ini file; no quotes

        if (item.message == item.payload) or (not (' ' in  item.message) and not (',' in item.message)):
            # if no format has been set, default to "value={payload}"
            # or if format has been set to output simple value, without additional tags or multiple fields
            # format = {json_attribute}
            data = measurement + ',' + tag + ' value=' + value

        elif (',' in item.message) and (not ' ' in item.message):
            # if format does not include any additional tags or a timestamp, but includes one or multiple non-default fields
            # format = field1=value1,field2=value2
            data = measurement + ',' + tag + ' ' + item.message

        else:
            # if format includes additional tags and one or multiple non-default fields and an optional timestamp, either group separated by whitespace from each other
            # format = tagKey1=tagVal1,tagKey2=tagVal2 field1=value1,field2=value2
            data = measurement + ',' + tag + ',' + item.message

        srv.logging.debug(url)
        srv.logging.debug(data)

        if username is None:
            r = requests.post(url, data=data)
        else:
            r = requests.post(url, data=data, auth=(username, password))
        
        # success
        if r.status_code == 204:
            return True
            
        # request accepted but couldn't be completed (200) or failed (otherwise)
        if r.status_code == 200:
            srv.logging.warn("POST request could not be completed: %s" % (r.text))
        else:
            srv.logging.warn("POST request failed: (%s) %s" % (r.status_code, r.text))
        
    except Exception as e:
        srv.logging.warn("Failed to send POST request to InfluxDB server using %s: %s" % (url, e))

    return False
