#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__    = 'Bram Hendrickx'
__copyright__ = 'Copyright 2016 Bram Hendrickx'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

Original script by Bram Hendrickx. https://github.com/jpmens/mqttwarn/blob/master/services/ifttt.py
Modified to work with notify-me app for Alexa. http://www.thomptronics.com/notify-me
"""

__author__ = 'Michael Brougham'
__copyright__ = 'Copyright 2018 Michael Brougham'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import json
import requests


def plugin(srv, item):
    """ expects (key) in addrs """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        srv.logging.debug("Sending to NotifyMe service.")
        body = json.dumps({
            "notification": item.message,
            "accessCode": item.addrs[0]
        })

        requests.post(url="https://api.notifymyecho.com/v1/NotifyMe", data=body)

        srv.logging.debug("Successfully sent to NotifyMe service.")

    except Exception as e:
        srv.logging.warning("Failed to send message to NotifyMe service." % e)
        return False

    return True
