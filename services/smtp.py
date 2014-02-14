#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: targets=%s, addrs=%s", __file__, item.targets, item.addrs)

    targets  = item.targets
    config   = item.config

    smtp_addresses = item.addrs

    server      = config['server']
    sender      = config['sender']
    starttls    = config['starttls']
    username    = config['username']
    password    = config['password']

    msg = MIMEText(item.get('message', item.payload))
    msg['Subject']      = item.get('title', "%s notification" % (srv.SCRIPTNAME))
    msg['From']         = sender
    msg['X-Mailer']     = srv.SCRIPTNAME

    try:
        srv.logging.debug("Sending SMTP notification to %s [%s]..." % (targets, smtp_addresses))
        server = smtplib.SMTP(server)
        server.set_debuglevel(0)
        server.ehlo()
        if starttls:
            server.starttls()
        if username:
            server.login(username, password)
        server.sendmail(sender, smtp_addresses, msg.as_string())
        server.quit()
        srv.logging.debug("Successfully sent SMTP notification")
    except Exception, e:
        srv.logging.warn("Error sending notification to SMTP recipient %s [%s]: %s" % (targets, smtp_addresses, str(e)))
        return

    return  
