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


import requests

def plugin(srv, item):
    ''' expects (URL) in addrs '''

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    try:
        srv.logging.debug("Sending to discord webhook")

	url = item.addrs[0]

	payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + item.message + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"username\"\r\n\r\n" + item.topic + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"tts\"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
	headers = {
    	    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    	    'Content-Type': "application/json",
    	    'Cache-Control': "no-cache",
   	    }

	response = requests.request("POST", url, data=payload, headers=headers)

	srv.loggin.debug(response.text)
	srv.logging.debug("Successfully sent to discord webhook")

    except Exception, e:
        srv.logging.warning("Failed to send message to discord webhook" % (str(e)))
        return False

    return True
