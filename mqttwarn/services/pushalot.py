#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The code for pushalot() plugin for mqttwarn is based on other plugins
# by Matthew Bordignon @bordignon on twitter 2014

from future import standard_library

standard_library.install_aliases()
from builtins import str
from urllib.parse import urlencode
from http.client import HTTPSConnection, HTTPException
from ssl import SSLError


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    apikey = item.addrs[0]

    title = item.get('title', srv.SCRIPTNAME)
    message = item.message

    http_handler = HTTPSConnection("pushalot.com")

    data = {'AuthorizationToken': apikey,
            'Title': title.encode('utf-8'),
            'Body': message.encode('utf-8')
            }

    try:
        http_handler.request("POST", "/api/sendmessage",
                             headers={'Content-type': "application/x-www-form-urlencoded"},
                             body=urlencode(data)
                             )
    except (SSLError, HTTPException) as e:
        srv.logging.warn("Pushalot notification failed: %s" % str(e))
        return False

    response = http_handler.getresponse()

    srv.logging.debug("Reponse: %s, %s" % (response.status, response.reason))

    return True
