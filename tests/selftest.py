# -*- coding: utf-8 -*-
# (c) 2018-2019 The mqttwarn developers


def foobar():
    return True


def xform_func(data):
    data['datamap-key'] = 'datamap-value'
    return data


def datamap_dummy(topic):
    return {'datamap-key': 'datamap-value'}


def alldata_dummy(topic):
    return {'alldata-key': 'alldata-value'}
