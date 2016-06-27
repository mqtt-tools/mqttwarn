#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The code for thingspeak plugin for mqttwarn is based on other plugins

from urllib import urlencode
from httplib import HTTPSConnection, HTTPException
from ssl import SSLError

__author__    = 'Marcel Verpaalen'
__copyright__ = 'Copyright 2015 Marcel Verpaalen'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

builddata = {}

def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    build = ""
    title = item.get('title', srv.SCRIPTNAME)
    message = item.message

    try:
      if len(item.addrs) == 3:
        apikey, field_id , build = item.addrs
      elif len(item.addrs) == 2:
        apikey, field_id = item.addrs
      else:
        srv.logging.warn("thingspeak target is incorrectly configured. use 2 or 3 arguments")
        return False
    except:
        srv.logging.warn("thingspeak target is incorrectly configured")
        return False

    if build == "true":
        builddata.update ({field_id: message.encode('utf-8')})
        srv.logging.debug("thingspeak content building. Update %s to '%s' stored for later submission." , field_id, message.encode('utf-8'))
        return True

    http_handler = HTTPSConnection("api.thingspeak.com")

    data = {'api_key': apikey,
            field_id: message.encode('utf-8')
            }
    if len (builddata) > 0:
        data.update (builddata)
        builddata.clear()

    try:
        http_handler.request("POST", "/update",
                         headers={'Content-type': "application/x-www-form-urlencoded"},
                         body=urlencode(sorted(data.items()))
                         )
    except (SSLError, HTTPException), e:
        srv.logging.warn("Thingspeak update failed: %s" % str(e))
        return False

    response = http_handler.getresponse()
    body = response.read()

    if body == '0':
        srv.logging.warn("Thingspeak channel '%s' field '%s' update failed. Reponse: %s, %s, %s" % (item.target, field_id, response.status, response.reason, body))
    else:
        srv.logging.debug("Reponse: %s, %s, update: %s" % (response.status, response.reason, body))

    return True
