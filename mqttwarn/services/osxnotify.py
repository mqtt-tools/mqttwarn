#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

from pync import Notifier


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    text = item.message
    application_name = item.get('title', item.topic)

    # If item.data contains a URL field, use it as a target for the notification
    url = None
    extra_data = item.data
    if extra_data is not None:
        url = extra_data.get('url', None)

    try:
        Notifier.notify(text,  title=application_name, open=url)
    except Exception as e:
        srv.logging.warning("Cannot invoke Notifier to osx: %s" % e)
        return False

    return True
