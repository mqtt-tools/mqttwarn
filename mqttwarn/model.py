# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import dataclasses
import platform
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Union
from mqttwarn import __version__


@dataclass
class ProcessorItem:
    """
    A processor item for feeding information into service handlers.
    """

    service: str = None
    target: str = None
    config: Dict = field(default_factory=dict)
    addrs: List[Union[str, Dict[str, str]]] = field(default_factory=list)
    priority: int = None
    topic: str = None
    title: str = None
    message: Union[str, bytes] = None
    data: Dict = None

    def asdict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class StatusInformation:
    """
    Different bits of information published to `mqttwarn/$SYS` when the `status_publish` feature is enabled.
    """
    mqttwarn_version: str = __version__
    os_platform: str = sys.platform
    python_version: str = platform.python_version()
