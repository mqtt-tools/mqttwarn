#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__ = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import twitter


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    twitter_keys = item.addrs

    twapi = twitter.Api(
        consumer_key=twitter_keys[0],
        consumer_secret=twitter_keys[1],
        access_token_key=twitter_keys[2],
        access_token_secret=twitter_keys[3]
    )

    text = item.message[0:138]
    try:
        srv.logging.debug("Sending tweet to %s..." % (item.target))
        res = twapi.PostUpdate(text, trim_user=False)
        srv.logging.debug("Successfully sent tweet")
    except twitter.TwitterError as e:
        srv.logging.error("TwitterError: %s" % e)
        return False
    except Exception as e:
        srv.logging.error("Error sending tweet to %s: %s" % (item.target, e))
        return False

    return True
