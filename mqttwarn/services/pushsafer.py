#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from future import standard_library
standard_library.install_aliases()
import os
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse

import typing as t

from mqttwarn.model import ProcessorItem

PUSHSAFER_API = "https://www.pushsafer.com/"


class PushsaferError(Exception): pass
class PushsaferConfigurationError(Exception): pass


def pushsafer(**kwargs):
    """
    Submit notification to Pushsafer.
    """
    assert 'm' in kwargs

    if not kwargs['k']:
        kwargs['k'] = os.environ['PUSHSAFER_TOKEN']

    url = urllib.parse.urljoin(PUSHSAFER_API, "api")
    data = urllib.parse.urlencode(kwargs).encode('utf-8')
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req, timeout=3)
    output = response.read()
    data = json.loads(output)

    if data['status'] != 1:
        raise PushsaferError(output)


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # Compute Pushsafer parameters from `ProcessorItem`.
    pe = PushsaferParameterEncoder(item=item)
    try:
        pe.encode()
    except PushsaferConfigurationError as ex:
        srv.logging.error(f"{ex}. target={item.target}")
        return False

    # Submit notification.
    params = pe.params
    try:
        srv.logging.debug("Sending pushsafer notification to %s [%s]..." % (item.target, params))
        pushsafer(m=item.message, k=pe.private_key, **params)
        srv.logging.debug("Successfully sent pushsafer notification")
    except Exception as e:
        srv.logging.warning("Error sending pushsafer notification to %s [%s]: %s" % (item.target, params, e))
        return False

    return True


class PushsaferParameterEncoder:
    """
    Encode Pushsafer parameters from mqttwarn configuration layout.
    """
    def __init__(self, item: ProcessorItem):
        self.item = item
        self.private_key: t.Optional[str] = None
        self.params: t.Dict[str, str] = {}

    def encode(self):
        addrs = self.item.addrs
        if isinstance(addrs, t.List):
            self.encode_v1()
        elif isinstance(addrs, t.Dict):
            raise NotImplementedError("Pushsafer configuration layout v2 not implemented yet")
        else:
            raise ValueError(f"Unable to decode Pushsafer configuration layout. type={type(addrs)}")

    def encode_v1(self):
        """
        Based on the Pushsafer API (https://www.pushsafer.com/en/pushapi).
        `addrs` is a list with two or three elements.

        0 is the private or alias key
        1 (if present) is the Pushsafer device or device group id where the message is to be sent
        2 (if present) is the Pushsafer icon to display in the message
        3 (if present) is the Pushsafer sound to play for the message
        4 (if present) is the Pushsafer vibration for the message
        5 (if present) is the Pushsafer URL or URL Scheme
        6 (if present) is the Pushsafer Title of URL
        7 (if present) is the Pushsafer Time in minutes, after which message automatically gets purged
        8 (if present) is the Pushsafer priority, integer -2, -1, 0, 1, 2
        9 (if present) is the Pushsafer retry after which time (in seconds 60-10800) a message should resend
        10 (if present) is the Pushsafer expire after which time (in seconds 60-10800) the retry should stopped
        11 (if present) is the Pushsafer answer, 1 = Answer, 0 = no possibility to answer
        """

        addrs = self.item.addrs
        title = self.item.title

        # Decode Private or Alias Key.
        try:
            self.private_key = addrs[0]
        except IndexError:
            raise PushsaferConfigurationError(f"Pushsafer private or alias key not configured")

        params = {
            'expire': 3600,
        }

        if len(addrs) > 1:
            params['d'] = addrs[1]

        if len(addrs) > 2:
            params['i'] = addrs[2]

        if len(addrs) > 3:
            params['s'] = addrs[3]

        if len(addrs) > 4:
            params['v'] = addrs[4]

        if len(addrs) > 5:
            params['u'] = addrs[5]

        if len(addrs) > 6:
            params['ut'] = addrs[6]

        if len(addrs) > 7:
            params['l'] = addrs[7]

        if len(addrs) > 8:
            params['pr'] = addrs[8]

        if len(addrs) > 9:
            params['re'] = addrs[9]

        if len(addrs) > 10:
            params['ex'] = addrs[10]

        if len(addrs) > 11:
            params['a'] = addrs[11]

        if title is not None:
            params['t'] = title

        self.params = params
