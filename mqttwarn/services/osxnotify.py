#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Alexander Gräf <portalzine.projects()gmail.com>'
__copyright__ = 'Copyright 2022 Alexander Gräf'
__version__   = '1.0.0'
__license__   = 'Eclipse Public License - v 2.0 - https://www.eclipse.org/legal/epl-2.0/'

import json
from desktop_notifier import DesktopNotifier, Urgency, Button, ReplyField

notify = DesktopNotifier()

def is_json(msg):
   try:
     json.loads(msg)
   except ValueError as e:
     return False
   return True

def plugin(srv, item):
    # Log
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # Load Config
    config = item.config

    # Play Sound ?
    playSound = True
    if isinstance(config, dict):
       playSound = config.get('sound', True)

    # Get Message
    message = item.message
    if is_json(message) == True:
       data = json.loads(message)
    else:
       data = {
         "title"  : item.get('title',item.topic),
         "message": message
       }

    srv.logging.debug("Sending desktop notification")
    try:
        # Synchronous Notification (allows no callbacks in OSX)
        # Asynchronous would require asyncio and require some changes to the plugin handler
        notify.send_sync(message=data['message'], title=data['title'],sound=playSound)

    except Exception as e:
        srv.logging.warning("Invoking OSX-Notifier failed: %s" % e)
        return False

    return True
