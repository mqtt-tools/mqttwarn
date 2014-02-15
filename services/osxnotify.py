#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

from pync import Notifier   # https://github.com/SeTem/pync
import os

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    text = item.get('message', item.payload)
    application_name = item.get('title', item.topic)

    try:
        Notifier.notify(text,  title=application_name)
    except Exception, e:
        srv.logging.warning("Cannot invoke Notifier to osx: %s" % (str(e)))

    return  





