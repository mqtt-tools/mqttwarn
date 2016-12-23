#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2016 Ben Jones'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

HAVE_REQUESTS = True
try:
    import requests                     # pip install requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    HAVE_REQUESTS = False

try:
    import json
except ImportError:
    import simplejson as json

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    if HAVE_REQUESTS == False:
        srv.logging.error("Missing module: requests")
        return False

    host          = item.config['host']
    port          = item.config['port']
    username      = item.config['username']
    password      = item.config['password']

    # optional ca-cert (usually self-signed cert installed by icinga2)
    if 'cacert' in item.config:
        cacert    = item.config['cacert']
    else:
        cacert    = None

    # e.g. example.com!ping4
    check_host    = item.addrs[0]
    check_service = item.addrs[1]
    check_source  = item.addrs[2]

    if check_service is None:
        check_type   = 'host'
        check_target = check_host
    else:
        check_type   = 'service'
        check_target = '{0}!{1}'.format(check_host, check_service)

    if check_source is None:
        check_source = 'mqttwarn'

    payload = {
        'exit_status'   : item.priority,
        'plugin_output' : item.message,
        'check_source'  : check_source,
        check_type      : check_target,
        }

    # update our payload with any JSON data in the mesage
    try:
        payload.update(json.loads(item.message))
    except Exception:
        pass

    # request parameters
    headers = {
        "Accept": "application/json"
        }

    kwargs = {
        "headers" : headers,
        "auth"    : HTTPBasicAuth(username, password),
        "json"    : payload
        }

    if cacert:
        kwargs[ "verify" ] = cacert

    try:
        url = "%s:%d/v1/actions/process-check-result" % (host, port)
        r = requests.post(url, **kwargs)
        if r.status_code != requests.codes.ok:
            srv.logging.warning("Invalid response from icinga2 REST API at `%s`: %s" % (host, r.text))
            return False
    except Exception, e:
        srv.logging.warning("Failed to POST request to icinga2 REST API at `%s': %s" % (host, str(e)))
        return False

    return True
