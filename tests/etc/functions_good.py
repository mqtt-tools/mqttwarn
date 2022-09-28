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
    data["xform-key"] = "xform-value"
    return data


def datamap_dummy_v1(topic):
    return {"datamap-key": "datamap-value"}


def datamap_dummy_v2(topic, srv):
    return {"datamap-key": "datamap-value"}


def alldata_dummy(topic, data, srv):
    return {"alldata-key": "alldata-value"}


def filter_dummy_v1(topic, message):
    do_skip = "reject" in message
    return do_skip


def filter_dummy_v2(topic, message, section, srv):
    do_skip = "reject" in message
    return do_skip


def get_targets_valid(srv, topic, data):
    return ["log:info"]


def get_targets_invalid(srv, topic, data):
    return ["log:invalid"]


def get_targets_broken(srv, topic, data):
    return "broken"


def get_targets_error(srv, topic, data):
    raise ValueError("Something failed")
