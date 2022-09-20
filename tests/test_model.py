# -*- coding: utf-8 -*-
# (c) 2022 The mqttwarn developers
from mqttwarn.core import Job


def test_sort_jobs_by_priority():
    job1 = Job(
        prio=1, service="service", section="section", topic="topic", payload="payload", data="data", target="target"
    )
    job2 = Job(
        prio=2, service="service", section="section", topic="topic", payload="payload", data="data", target="target"
    )

    assert sorted([job2, job1]) == [job1, job2]
