#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from builtins import str
import socket
import struct

# Single file, imported from https://github.com/BlueSkyDetector/code-snippet/tree/master/ZabbixSender
# Lincense: DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                     Version 2, December 2004
# Copyright (C) 2010 Takanori Suzuki

# JPM: s/simplejson/json/g

try:
    import json
except ImportError:
    import simplejson as json  # type: ignore[no-redef]


class ZabbixSender:
    
    zbx_header = b'ZBXD'
    zbx_version = 1
    zbx_sender_data = {'request': 'sender data', 'data': []}
    send_data = ''
    
    def __init__(self, server_host, server_port = 10051):
        self.server_ip = socket.gethostbyname(server_host)
        self.server_port = server_port
    
    def AddData(self, host, key, value, clock = None):
        add_data = {'host': host, 'key': key, 'value': value}
        if clock != None:
            add_data['clock'] = clock
        self.zbx_sender_data['data'].append(add_data)
        return self.zbx_sender_data
    
    def ClearData(self):
        self.zbx_sender_data['data'] = []
        return self.zbx_sender_data
    
    def __MakeSendData(self):
        zbx_sender_json = json.dumps(self.zbx_sender_data, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        json_byte = len(zbx_sender_json)
        self.send_data = struct.pack("<4sBq" + str(json_byte) + "s", self.zbx_header, self.zbx_version, json_byte, zbx_sender_json)
    
    def Send(self):
        self.__MakeSendData()
        so = socket.socket()
        so.connect((self.server_ip, self.server_port))
        wobj = so.makefile('wb')
        wobj.write(self.send_data)
        wobj.close()
        robj = so.makefile('rb')
        recv_data = robj.read()
        robj.close()
        so.close()
        tmp_data = struct.unpack("<4sBq" + str(len(recv_data) - struct.calcsize("<4sBq")) + "s", recv_data)
        recv_json = json.loads(tmp_data[3])
        #JPM return recv_data
        return recv_json


if __name__ == '__main__':
    sender = ZabbixSender('127.0.0.1')
    for num in range(0, 2):
        sender.AddData('HostA', 'AppX_Logger', 'sent data 第' + str(num))
    res = sender.Send()
    print(sender.send_data)
    print(res)
