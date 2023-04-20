# -*- coding: utf-8 -*-
# (c) 2021-2023 The mqttwarn developers
from __future__ import absolute_import

from functools import lru_cache
from urllib.parse import urlparse, urlencode

from apprise import Apprise, ContentLocation

from mqttwarn.model import ProcessorItem


@lru_cache(maxsize=None)
def get_all_template_argument_names():
    """
    Inquire all possible parameter names from all Apprise plugins.
    """
    a = Apprise(asset=None, location=ContentLocation.LOCAL)
    results = a.details()
    plugin_infos = results['schemas']

    all_arg_names = []
    for plugin_info in plugin_infos:
        arg_names = plugin_info["details"]["args"].keys()
        all_arg_names += arg_names

    return sorted(set(all_arg_names))


def obtain_apprise_arguments(item: ProcessorItem, arg_names: list) -> dict:
    """
    Obtain eventual Apprise parameters from data dictionary.
    """
    params = dict()
    for arg_name in arg_names:
        if isinstance(item.data, dict) and arg_name in item.data:
            params[arg_name] = item.data[arg_name]
    return params


def add_url_params(url: str, params: dict) -> str:
    """
    Serialize query parameter dictionary and add it to URL.
    """
    url_parsed = urlparse(url)
    if params:
        seperator = "?"
        if url_parsed.query:
            seperator = "&"
        url += seperator + urlencode(params)
    return url
