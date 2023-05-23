#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import requests


def plugin(srv, item):
    """
    mqttwarn service for Pushbullet notifications.
    """

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    # Decode target address descriptor.
    if isinstance(item.addrs, list):
        try:
            apikey, device_id = item.addrs
            options = {"access_token": apikey, "recipient": device_id}
        except:
            try:
                apikey, device_id, recipient_type = item.addrs
                options = {"access_token": apikey, "recipient": device_id, "recipient_type": recipient_type}
            except:
                raise ValueError("Pushbullet target is incorrectly configured")
    elif isinstance(item.addrs, dict):
        options = item.addrs
    else:
        raise ValueError(f"Unknown target address descriptor type: {type(item.addrs).__name__}")

    # Assemble keyword arguments for `send_note` function.
    text = item.message
    title = item.get('title', srv.SCRIPTNAME)
    options.update({"title": title, "body": text})

    try:
        srv.logging.debug(f"Sending Pushbullet notification to {item.target}")
        send_note(**options)
        srv.logging.debug("Successfully sent Pushbullet notification")
    except Exception:
        srv.logging.exception("Sending Pushbullet notification failed")
        return False

    return True


def send_note(access_token, title, body, recipient, recipient_type="device"):
    """
    Send a Pushbullet message with type=note.

    https://docs.pushbullet.com/#push
    """
    headers = {
        "Access-Token": access_token,
        "Content-Type": "application/json",
        "User-Agent": "mqttwarn",
    }
    data = {"type": "note", "title": title, "body": body}
    if recipient_type is None:
        pass
    elif recipient_type == "device":
        data["device_iden"] = recipient
    elif recipient_type == "email":
        data["email"] = recipient
    elif recipient_type == "channel":
        data["channel_tag"] = recipient
    elif recipient_type == "client":
        data["client_iden"] = recipient
    else:
        raise ValueError(f"Unknown recipient type: {recipient_type}")

    response = requests.post("https://api.pushbullet.com/v2/pushes", headers=headers, json=data)
    response.raise_for_status()

    return response.status_code == requests.codes.ok
