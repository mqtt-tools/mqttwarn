#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Alexander Gräf <portalzine.projects()gmail.com>'
__copyright__ = 'Copyright 2022 Alexander Gräf'
__version__   = '1.0.0'
__license__   = 'Eclipse Public License - v 2.0 - https://www.eclipse.org/legal/epl-2.0/'

import json
import typing as t

from desktop_notifier import DesktopNotifier, Urgency, Button, ReplyField

from mqttwarn.model import Service, ProcessorItem, Struct

notify = DesktopNotifier()

def is_json(msg: t.Union[str, bytes]) -> bool:
   try:
     json.loads(msg)
   except ValueError as e:
     return False
   return True

def plugin(srv: Service, item: ProcessorItem):
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
    if message and is_json(message):
       data = json.loads(message)
    else:
       data = {
         "title"  : item.get('title', item.topic),
         "message": message
       }

    srv.logging.debug("Sending desktop notification")
    try:
        # Synchronous Notification (allows no callbacks in OSX)
        # Asynchronous would require asyncio and require some changes to the plugin handler
        notify.send_sync(message=data['message'], title=data['title'],sound=playSound)

    except Exception as e:
        srv.logging.warning("Invoking desktop notifier failed: %s" % e)
        return False

    return True
