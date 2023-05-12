"""
Forward OwnTracks low-battery warnings to ntfy.
https://mqttwarn.readthedocs.io/en/latest/examples/owntracks-ntfy/readme.html
"""
import json


def owntracks_batteryfilter(topic: str, message: str):
    ignore = True
    try:
        data = dict(json.loads(message).items())
    except:
        data = None

    if data and "batt" in data and data["batt"] is not None:
        ignore = int(data["batt"]) > 20

    return ignore
