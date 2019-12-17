#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Orhan Hirsch <orhanhenrik()gmail.com>'
__copyright__ = 'Copyright 2017 Orhan Hirsch'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import json
import celery


def plugin(srv, item):
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    config = item.config

    app = celery.Celery(
        config['app_name'],
        broker=config['broker_url']
    )

    for target in item.addrs:
        message = item.message
        try:
            if target['message_format'] == 'json':
                message = json.loads(message)
            app.send_task(target['task'], [message])
        except Exception as e:
            srv.logging.warning("Error: %s" % e)
            return False

    return True
