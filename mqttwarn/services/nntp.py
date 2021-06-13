#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = 'Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)'

import nntplib
from six import StringIO
from email.mime.text import MIMEText
from email.utils import formatdate


def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    host      = item.config.get('server', 'localhost')
    port      = item.config.get('port', 119)
    username  = item.config.get('username')
    password  = item.config.get('password')

    try:
        from_hdr = item.addrs[0]
        newsgroup = item.addrs[1]
    except Exception:
        srv.logging.error("Incorrect target configuration for %s" % item.target)
        return False

    try:

        text  = item.message
        title    = item.title

        msg = MIMEText(text)

        msg['From']         = from_hdr
        msg['Subject']      = item.title
        msg['Newsgroups']   = newsgroup
        msg['Date']         = formatdate()
        msg['User-Agent']   = srv.SCRIPTNAME
        # msg['Message-ID'] = '<jp001@tiggr>'

        msg_file = StringIO(msg.as_string())
        nntp = nntplib.NNTP(host, port, user=username, password=password)

        srv.logging.debug(nntp.getwelcome())
        nntp.set_debuglevel(0)

        nntp.post(msg_file)
        nntp.quit()
    except Exception as e:
        srv.logging.warn("Cannot post to %s newsgroup: %s" % (newsgroup, e))
        return False

    return True
