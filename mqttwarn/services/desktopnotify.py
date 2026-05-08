#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Alexander Gräf <portalzine.projects()gmail.com>'
__copyright__ = 'Copyright 2022 Alexander Gräf'
__version__   = '1.0.0'
__license__   = 'Eclipse Public License - v 2.0 - https://www.eclipse.org/legal/epl-2.0/'

import json
import typing as t
import asyncio

from desktop_notifier import DesktopNotifier, Urgency, Button, ReplyField

from mqttwarn.model import Service, ProcessorItem, Struct


notify = DesktopNotifier()


def is_json(msg: t.Union[str, bytes]) -> bool:
   try:
     json.loads(msg)
   except ValueError as e:
     return False
   except TypeError as e:
     return False
   return True


async def send_notification(message, title, sound=True):
   await notify.send(message=message, title=title, sound=sound)


def plugin(srv: Service, item: ProcessorItem):
    # Log
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # Load Config
    config = item.config

    # Play Sound ?
    playSound = False
    if isinstance(config, dict):
       playSound = config.get('sound', False)

    # Get Message
    message = item.message
    if message is None:
        raise ValueError("Message is required")
    if is_json(message):
       parsed = json.loads(message)
       data = parsed if isinstance(parsed, dict) else {
         "title": item.get("title", item.topic),
         "message": parsed,
       }
    else:       
       try:
          msg = t.cast(t.Dict, message).get('message')
       except:
          msg = str(message)
       data = {
         "title"  : item.get('title', item.topic),
         "message": msg
       }

    srv.logging.debug("Sending desktop notification")
    message = str(data.get('message', ''))
    title = str(data.get('title', ''))
    try:
        # TODO: Fix issue where this keeps running until the notification is closed.
        asyncio.run(send_notification(message=message, title=title, sound=playSound))

    except Exception as e:
        srv.logging.warning("Invoking desktop notifier failed: %s" % e)
        return False

    return True
