# -*- coding: utf-8 -*-
import time
import copy
import ast
from datetime import datetime

def powerBinFunc(topic, data, srv=None):
    # parse json payload (the message)
    payload = ast.literal_eval(data["payload"])

    # Override default time format
    dt = datetime.strptime(payload["Time"], '%Y-%m-%dT%H:%M:%S')
    ts = time.mktime(dt.timetuple())
    ret = dict( payload = dict( Time = ts ))

    # Check power state key
    if "POWER" in payload:
        if payload["POWER"] == "ON":
            ret["POWER_BIN"] = 1
        else:
            ret["POWER_BIN"] = 0

    return ret

# vim: tabstop=4 expandtab
