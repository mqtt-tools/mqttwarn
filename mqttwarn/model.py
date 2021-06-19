# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class ProcessorItem:
    """
    A processor item for feeding information into service handlers.
    """

    service: str = None
    target: str = None
    config: Dict = None
    addrs: List[str] = None
    priority: int = None
    topic: str = None
    title: str = None
    message: Union[str, bytes] = None
    data: Dict = None
