# -*- coding: utf-8 -*-
# (c) 2018-2022 The mqttwarn developers
import logging

logger = logging.getLogger(__name__)


def foobar():
    return True


def cronfunc(srv):
    logger.info("`cronfunc` called")
    return True


def xform_func(data):
    data["datamap-key"] = "datamap-value"
    return data


def datamap_dummy(topic):
    return {"datamap-key": "datamap-value"}


def alldata_dummy(topic):
    return {"alldata-key": "alldata-value"}


def get_targets_valid(srv, topic, data):
    return ["log:info"]


def get_targets_invalid(srv, topic, data):
    return ["log:invalid"]


def get_targets_broken(srv, topic, data):
    return "broken"
