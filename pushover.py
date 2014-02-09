#!/usr/bin/env python

import urllib
import urllib2
import urlparse
import json
import os

PUSHOVER_API = "https://api.pushover.net/1/"

class PushoverError(Exception): pass

def pushover(**kwargs):
    assert 'message' in kwargs

    if not 'token' in kwargs:
        kwargs['token'] = os.environ['PUSHOVER_TOKEN']
    if not 'user' in kwargs:
        kwargs['user'] = os.environ['PUSHOVER_USER']

    url = urlparse.urljoin(PUSHOVER_API, "messages.json")
    data = urllib.urlencode(kwargs)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    output = response.read()
    data = json.loads(output)

    if data['status'] != 1:
        raise PushoverError(output)
