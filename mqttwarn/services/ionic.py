#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'hubble2webb <hubble2webb@users.noreply.github.com>'
__copyright__ = 'Copyright 2015 hubble2webb'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()
from builtins import str

import urllib.request, urllib.error, urllib.parse
import base64

try:
    import simplejson as json
except ImportError:
    import json  # type: ignore[no-redef]


def plugin(srv, item):
    # item.addrs is an array with three or more elements:
    # 0 is the Ionic appid
    # 1 is the Ionic appsecret (private key)
    # 2..N are the push tokens returned by Ionic push service

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    if len(item.addrs) < 3:
        srv.logging.error("appid, appsecret and atleast one devicetoken is required")
        return False

    appid = item.addrs[0]
    appsecret = item.addrs[1]
    devicetokens = item.addrs[2:]

    if not appid or appid.isspace():
        srv.logging.error("appid is missing or empty")
        return False
    if not appsecret or appsecret.isspace():
        srv.logging.error("appsecret is missing or empty")
        return False
    if len(devicetokens) == 0:
        srv.logging.error("atleast one devicetoken is required")
        return False

    devicetokens = [_f for _f in devicetokens if _f]
    devicetokens = [name for name in devicetokens if name.strip()]
    appid = appid.strip()
    appsecret = appsecret.strip()


    data = {"tokens": devicetokens}
    notification = {"alert": item.message}
    data["notification"] = notification

    resource = "https://push.ionic.io/api/v1/push"

    try:
        handler = urllib.request.HTTPHandler()
        opener = urllib.request.build_opener(handler)

        credentials = '%s:' % (appsecret)
        basicauth_token = base64.b64encode(credentials.encode('utf-8')).decode()

        data = json.dumps(data)
        request = urllib.request.Request(resource, data=data.encode("utf-8"))
        request.add_header('X-Ionic-Application-Id', appid)
        request.add_header("Authorization", "Basic %s" % basicauth_token)
        request.add_header("Content-Type", 'application/json')

        connection = opener.open(request, timeout=5)
        srv.logging.info("Server reply: %s" % str(connection.read()))

    except urllib.error.HTTPError as e:
        srv.logging.warn("Failed to send POST request to ionic using %s: %s" % (resource, str(e.read())))
        return False

    return True
