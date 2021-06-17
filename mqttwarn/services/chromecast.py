#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Text To Speech (TTS) for Chromecast devices, including Google Home Speakers

pip install pychromecast

See also https://github.com/skorokithakis/catt.
"""

__author__ = 'Chris Clark <clach04()gmail.com>'
__copyright__ = 'Copyright 2020 Chris Clark'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'


import os
from urllib.parse import urlencode


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    message = item.message
    mime_type = item.config.get('mimetype', 'audio/mp3')  # Google translate emits mp3, NOTE Chromecast devices appear to  not care if incorrect
    base_url = item.config.get('baseuri', os.environ.get('GOOGLE_TRANSLATE_URL', 'https://translate.google.com/translate_tts?'))
    lang = item.config.get('lang', 'en')  # English

    # Generate a Google Translate (compatible) URL to generate TTS
    vars = {
        'q': message,
        'l': lang,
        'tl': lang,
        'client': 'tw-ob',
        'ttsspeed': 1,
        'total': 1,
        'ie': 'UTF-8',
        # looks like can get away with out 'textlen'
    }
    url = base_url + urlencode(vars)


    # TODO disable pychromecast library logging?
    import pychromecast  # Some plugin systems want lazy loading, defer import until about to use it

    chromecasts, browser  = pychromecast.get_listed_chromecasts(friendly_names=item.addrs)
    if not chromecasts:
        return False
    for cast in chromecasts:
        cast.wait()
        #srv.logging.debug("cast=%r", cast)
        """
        print('%r' % (cast.device.friendly_name,))
        print('%r' % (cast.socket_client.host,))
        """
        mc = cast.media_controller
        mc.play_media(url, content_type=mime_type)
        mc.block_until_active()
        mc.play()  # issue play, return immediately
        # TODO detect when play failed
        # if one end point works, but another fails is that a success or a failure?
        # What is an end point does NOT show up in list? i.e. len(item.addrs) > len(chromecasts)

    return True

