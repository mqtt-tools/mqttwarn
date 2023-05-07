# -*- coding: utf-8 -*-
# (c) 2018-2022 The mqttwarn developers
from copy import deepcopy

from mqttwarn.core import make_service
from mqttwarn.model import Job, ProcessorItem, Struct

JOB_PRIO1 = dict(
    prio=1, service="service", section="section", topic="topic", payload="payload", data="data", target="target"
)
JOB_PRIO2 = dict(
    prio=2, service="service", section="section", topic="topic", payload="payload", data="data", target="target"
)
JOB_PRIO1_COPY = deepcopy(JOB_PRIO1)


def test_make_service():
    """
    Verify creation of `Service` instance.
    """
    service = make_service(name="foo")
    assert "<mqttwarn.model.Service object at" in str(service)


def test_job_equality():
    """
    Test comparing `Job` instances for equality.
    """
    job1 = Job(**JOB_PRIO1)
    job2 = Job(**JOB_PRIO1_COPY)

    assert job1 == job2


def test_job_inequality():
    """
    Test comparing `Job` instances for inequality.
    """
    job1 = Job(**JOB_PRIO1)
    job2 = Job(**JOB_PRIO2)

    assert job1 != job2


def test_job_ordering_by_priority():
    """
    Test sorting a list of `Job` instances by priority.
    """
    job1 = Job(**JOB_PRIO1)
    job2 = Job(**JOB_PRIO2)

    assert sorted([job2, job1]) == [job1, job2]


def test_struct():
    data = {"hello": "world"}
    struct = Struct(**data)
    assert struct.hello == "world"
    assert struct.get("hello") == "world"
    assert struct.get("unknown", default=42) == 42
    assert repr(struct) == "<hello: 'world'>"
    assert struct.enum() == data


def test_processoritem():
    item = ProcessorItem()
    assert item.asdict() == {
        "service": None,
        "target": None,
        "config": {},
        "addrs": [],
        "priority": None,
        "section": None,
        "topic": None,
        "title": None,
        "message": None,
        "data": None,
    }
    assert item.get("foo") is None
