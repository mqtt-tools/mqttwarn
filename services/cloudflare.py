#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'David Cole <psyciknz()andc.co.nz>'
__copyright__ = 'Copyright 2019 David Cole'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

# Cloudflare DNS update.  Based on the http class from Jpmens, sumnerboy

import requests
import base64
try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):
    ''' addrs: (email, api_key, zone, records, ip_address) '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    email       = item.config['auth-email']
    api_key     = item.config['auth-key']
    zone        = item.addrs[0] #item.config['zone']
    if len(item.addrs) > 1: record_name = item.addrs[1] # 'all' or a named item
    if len(item.addrs) > 2: 
        record_id   = item.addrs[2] # 'all' or a named item
    else:
        record_id = ''

    ip          = item.message
    #timeout = item.config.get('timeout', 60)
    # 
    srv.logging.info('Service={}-Received Request for Zone "{}" Record Name "{}" Record ID "{}" for IP "{}"'.format(item.service,zone,record_name,record_id,ip))
    url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(zone)
    if len(record_name) > 0 and not record_name == 'all':
        url += '?type=A&name={}'.format(record_name)
    elif len(record_id) > 0:
        url += '/{}'.format(record_id) 
    else:
        url += '?type=A'
    #list all type a records
    resp = requests.get(
        url,
        headers={
            'X-Auth-Key': api_key,
            'X-Auth-Email': email
        })
    
    srv.logging.info(json.dumps(resp.json(), indent=4, sort_keys=True))

    jsondata = resp.json
    try:
        jsondata.__getitem__
    except AttributeError:
        jsondata = resp.json()
    
    if jsondata['success'] != True:
        raise Exception(json['msg'])
    if type(jsondata['result']) is list:
        for record in jsondata['result']:
            update_record(srv,email,api_key,zone,ip,record)
    elif type(jsondata['result']) is dict:
        update_record(srv,email,api_key,zone,ip,jsondata['result'])

        
    return True

def update_record(srv,email, api_key,zone,ip,record):
    if record['type'] == 'A' and record['content'] == ip:
            srv.logging.info("No IP Address update needed for record:" + record['name'] + " Address: " + ip)
    elif record['type'] == 'A':
        srv.logging.info("IP Address needs update for record:" + record['name'] + " from: " + record['content'] + " to: " + ip )
        resp = requests.put(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(
                zone, record['id']),
            json={
                'type': 'A',
                'content': ip,
                'name': record['name'],
                "ttl":1,
                "proxied":True
            },
            headers={
                'X-Auth-Key': api_key,
                'X-Auth-Email': email
            })
        if resp.status_code != 200:
            srv.logging.error("Error updating ip address of {} ({}) to {} - response received {}".format(record['name'],
                record['id'],ip,resp.status_code))
            return False