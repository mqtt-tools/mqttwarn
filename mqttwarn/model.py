# -*- coding: utf-8 -*-
# (c) 2021-2023 The mqttwarn developers
import dataclasses
import platform
import sys
import typing as t
from dataclasses import dataclass, field
from functools import total_ordering
from logging import Logger
from typing import Dict, Optional, Union

from mqttwarn import __version__

# Type definitions.

# The venerable transformation data dictionary.
TdataType = t.Dict[str, t.Union[t.AnyStr, int]]

# Covering old- and new-style configuration layouts. `addrs` has
# originally been a list of strings, has been expanded to be a
# list of dictionaries (Apprise), to be a dictionary (Pushsafer),
# and finally to be a scalar string only (ntfy).
TopicTargetType = t.Union[t.List, t.Dict[str, t.Any], str, None]


class Struct:
    """
    Data container for feeding information into service plugins - V1.
    """

    # Convert Python dict to object?
    # http://stackoverflow.com/questions/1305532/

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        return "<%s>" % str("\n ".join("%s: %s" % (k, repr(v)) for (k, v) in list(self.__dict__.items())))

    def get(self, key, default=None):
        if key in self.__dict__ and self.__dict__[key] is not None:
            return self.__dict__[key]
        else:
            return default

    def enum(self):
        item = {}
        for (k, v) in list(self.__dict__.items()):
            item[k] = v
        return item


@dataclass
class ProcessorItem:
    """
    Data container for feeding information into service plugins - V2.
    """

    service: Optional[str] = None
    target: Optional[str] = None
    config: Dict = field(default_factory=dict)
    section: Optional[str] = None
    # TODO: `addrs` can also be a string or dictionary now.
    addrs: TopicTargetType = field(default_factory=list)  # type: ignore[assignment]
    priority: Optional[int] = None
    topic: Optional[str] = None
    title: Optional[str] = None
    message: Optional[Union[str, bytes]] = None
    data: Optional[Dict] = None

    def asdict(self):
        return dataclasses.asdict(self)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def to_job(self) -> "Job":
        return Job(
            prio=self.priority,
            service=self.service,
            section=self.section,
            topic=self.topic,
            payload=self.message,
            data=self.data,
            target=self.target,
        )


@dataclasses.dataclass
class StatusInformation:
    """
    Different bits of information published to `mqttwarn/$SYS` when the `status_publish` feature is enabled.
    """

    mqttwarn_version: str = __version__
    os_platform: str = sys.platform
    python_version: str = platform.python_version()


class Service:
    """
    Class with helper functions which is passed to each plugin and its global instantiation.
    """

    def __init__(self, mqttc, logger, mwcore, program):

        # Reference to MQTT client object.
        self.mqttc = mqttc

        # Reference to all mqttwarn globals, for using its machinery from plugins.
        self.mwcore = mwcore

        # Reference to logging object.
        self.logging: Logger = logger  # type: ignore[annotation-unchecked]

        # Name of self ("mqttwarn", mostly).
        self.SCRIPTNAME = program


@total_ordering
class Job:
    def __init__(self, prio, service, section, topic, payload, data, target):
        self.prio = prio
        self.service = service
        self.section = section
        self.topic = topic
        self.payload = payload  # raw payload
        self.data = data  # decoded payload
        self.target = target

    # The `__cmp__()` special method is no longer honored in Python 3.
    # https://portingguide.readthedocs.io/en/latest/comparisons.html#rich-comparisons

    def __eq__(self, other):
        return self.prio == other.prio

    def __ne__(self, other):
        return not (self.prio == other.prio)

    def __lt__(self, other):
        return self.prio < other.prio
