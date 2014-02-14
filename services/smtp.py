#!/usr/bin/env python

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: targets=%s, addrs=%s", __file__, item.targets, item.addrs)

    topic    = item.topic
    payload  = item.payload
    addrs    = item.addrs
    targets  = item.targets
    title    = item.title
    priority = item.priority
    fmt      = item.fmt
    config   = item.config


    print config


    return  
