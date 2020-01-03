#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Artem Alexandrov <qk4l@tem4uk.ru>'
__copyright__ = 'Copyright 2016 Artem Alexandrov'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'


from builtins import str
from builtins import object
import requests
try:
    import simplejson as json
except ImportError:
    import json


def plugin(srv, item):
    """
    addrs: (tg_contact, token, text)
    """
    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    token = item.config['token']
    if 'use_chat_id' in item.config:
        useChatId = int(item.config.get('use_chat_id', 0))
    else:
        useChatId = False
    if 'parse_mode' in item.config:
        parse_mode = item.config['parse_mode']
    tg_contact = item.addrs[0]

    class TelegramAPI(object):
        def __init__(self, token, parse_mode=None):
            self.token = token
            self.disable_notification = False
            self.parse_mode = parse_mode
            self.tg_url_bot_general = "https://api.telegram.org/bot"

        def http_get(self, url):
            res = requests.get(url)
            answer = res.text
            answer_json = json.loads(answer.decode('utf8'))
            return answer_json

        def get_updates(self):
            """
            Get updates
            :return: Dict of last bot update
            """
            url = self.tg_url_bot_general + self.token + "/getUpdates"
            srv.logging.debug(url)
            updates = self.http_get(url)
            #srv.logging.debug("Content of /getUpdates: %s" % updates)
            if not updates["ok"]:
                srv.logging.warn(updates)
                return False
            else:
                return updates

        def get_uid(self, name):
            """
            Get chat_id for specific user
            :param name: First Name or @username of user or #chat_id
            :return: string
            """
            if name.startswith('#'):
                #chat_id was specified in mqttwarn.ini
                return name[1:]
            uid = 0
            srv.logging.debug("Getting uid from /getUpdates...")
            updates = self.get_updates()
            if name.startswith('@'):
                name = name[1:]
                name_type = 'username'
            else:
                name_type = 'first_name'
            for msg in updates["result"]:
                chat = msg["message"]["chat"]
                if name_type in chat:
                    if chat[name_type] == name:
                        uid = chat["id"]
                        break
            srv.logging.debug("For user {name} follow chat_id was found: {chat_id}".format(chat_id=uid,
                                                                                           name=name))
            return uid

        def send_message(self, chat_id, message):
            """
            Send message to chat_id
            :param chat_id: int
            :param message: string
            :return: Boolean
            """
            url = self.tg_url_bot_general + self.token + "/sendMessage"
            params = {"chat_id": chat_id, "text": message,
                      "parse_mode": self.parse_mode, "disable_notification": self.disable_notification}
            srv.logging.debug("Trying to /sendMessage: {url}".format(url=url))
            srv.logging.debug("post params: " + str(params))
            res = requests.post(url, params=params)
            answer = res.text
            answer_json = json.loads(answer.decode('utf8'))
            if not answer_json["ok"]:
                srv.logging.warn(answer_json)
                return False
            else:
                return answer_json

    try:
        tg = TelegramAPI(token, parse_mode)
        if useChatId:
            srv.logging.debug("Setting chatid directly to %s" % tg_contact)
            uid = int(tg_contact)
        else:
            uid = tg.get_uid(tg_contact)
        if uid == 0:
            srv.logging.warn("Cannot get chat_id for user %s" % tg_contact)
            return False
        reply = tg.send_message(uid, item.message)
        srv.logging.debug("Telegram reply: %s" % reply)
        if 'ok' in reply and reply['ok']:
            return True
        return False
    except:
        srv.logging.warn("Failed to send request to Telegram")
        return False
