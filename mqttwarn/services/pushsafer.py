#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import dataclasses
from collections import OrderedDict

import os
import json

try:
    from urllib.parse import urlparse, urlencode, urljoin
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse  # type: ignore[no-redef]
    from urllib import urlencode, urljoin  # type: ignore[no-redef,attr-defined]
    from urllib2 import urlopen, Request, HTTPError  # type: ignore[no-redef]

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

    # Don't submit empty parameters to Pushsafer.
    filter_empty_parameters(kwargs)

    url = urljoin(PUSHSAFER_API, "api")
    data = urlencode(kwargs).encode('utf-8')
    req = Request(url, data)
    response = urlopen(req, timeout=3)
    output = response.read()
    data = json.loads(output)

    if data['status'] != 1:
        raise PushsaferError(output)


def filter_empty_parameters(params: t.Dict[str, str]):
    """
    Filter empty parameters.
    """
    for key in list(params.keys()):
        value = params[key]
        if value == "":
            del params[key]


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
            self.encode_v2()
        else:
            raise ValueError(f"Pushsafer configuration layout empty or invalid. type={type(addrs).__name__}")

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
        12 (if present) is the Pushsafer answer options seperated by a pipe character e.g. yes|no|maybe
        13 (if present) is the Pushsafer force answer, 1 = yes, 0 = no
        14 (if present) is the Pushsafer message will be repeated after specified time delay when not confirmed
        """

        addrs = self.item.addrs
        title = self.item.title

        # Decode Private or Alias Key.
        try:
            self.private_key = addrs[0]
        except IndexError:
            raise PushsaferConfigurationError(f"Pushsafer private or alias key not configured")

        params = OrderedDict()

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

        if len(addrs) > 12:
            params['ao'] = addrs[12]

        if len(addrs) > 13:
            params['af'] = addrs[13]

        if len(addrs) > 14:
            params['cr'] = addrs[14]

        if title is not None:
            params['t'] = title

        self.params = params

    def encode_v2(self):
        """
        New-style configuration layout with named parameters for Pushsafer.
        """

        addrs = self.item.addrs
        title = self.item.title

        # Decode Private or Alias Key.
        try:
            self.private_key = addrs["private_key"]
        except KeyError:
            raise PushsaferConfigurationError(f"Pushsafer private or alias key not configured")

        # Decode and serialize all other parameters.
        pp = PushsaferParameters(**addrs)
        params = pp.translated()

        # Propagate `title` separately.
        if title is not None:
            params['t'] = title

        self.params = params


@dataclasses.dataclass
class PushsaferParameters:
    """
    Manage available Pushsafer parameters, and map them to their short representations,
    suitable for sending over the wire.

    - https://www.pushsafer.com/en/pushapi
    - https://www.pushsafer.com/en/pushapi_ext
    """
    private_key: t.Optional[str] = None
    device: t.Optional[str] = None
    icon: t.Optional[int] = None
    sound: t.Optional[int] = None
    vibration: t.Optional[int] = None
    url: t.Optional[str] = None
    url_title: t.Optional[str] = None
    time_to_live: t.Optional[int] = None
    priority: t.Optional[int] = None
    retry: t.Optional[int] = None
    expire: t.Optional[int] = None
    answer: t.Optional[int] = None
    answer_options: t.Optional[str] = None
    answer_force: t.Optional[int] = None
    confirm_repeat: t.Optional[int] = None

    PARAMETER_MAP = {
        "device": "d",
        "icon": "i",
        "sound": "s",
        "vibration": "v",
        "url": "u",
        "url_title": "ut",
        "time_to_live": "l",
        "priority": "pr",
        "retry": "re",
        "expire": "ex",
        "answer": "a",
        "answer_options": "ao",
        "answer_force": "af",
        "confirm_repeat": "cr",
    }

    def to_dict(self) -> t.Dict[str, t.Union[str, int]]:
        return dataclasses.asdict(self)

    def translated(self) -> t.Dict[str, t.Union[str, int]]:
        """
        Translate parameters to their wire representations.
        """
        result = OrderedDict()
        for attribute, parameter_name in self.PARAMETER_MAP.items():
            value = getattr(self, attribute)
            if value is not None:
                result[parameter_name] = value
        return result
