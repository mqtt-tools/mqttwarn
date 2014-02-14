#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pushover import pushover     # https://github.com/pix0r/pushover
import paho.mqtt.client as paho   # pip install paho-mqtt
import logging
import signal
import sys
import time
import os
import smtplib
from email.mime.text import MIMEText

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>, Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

# script name (without extension) used for config/logfile names
SCRIPTNAME = os.path.splitext(os.path.basename(__file__))[0]

CONFIGFILE = os.getenv(SCRIPTNAME.upper() + 'CONF', SCRIPTNAME + '.conf')
LOGFILE    = os.getenv(SCRIPTNAME.upper() + 'LOG', SCRIPTNAME + '.log')

# load configuration
conf = {}
try:
    execfile(CONFIGFILE, conf)
except Exception, e:
    print "Cannot load %s: %s" % (CONFIGFILE, str(e))
    sys.exit(2)

LOGLEVEL = conf.get('loglevel', logging.DEBUG)
LOGFORMAT = conf.get('logformat', '%(asctime)-15s %(message)s')

MQTT_HOST = conf.get('broker', 'localhost')
MQTT_PORT = int(conf.get('port', 1883))
MQTT_LWT = conf.get('lwt', None)

# initialise logging    
logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
logging.info("Starting %s" % SCRIPTNAME)
logging.info("INFO MODE")
logging.debug("DEBUG MODE")

# initialise MQTT broker connection
mqttc = paho.Client(SCRIPTNAME, clean_session=False)

# check for authentication
if conf['username'] is not None:
    mqttc.username_pw_set(conf['username'], conf['password'])

# configure the last-will-and-testament if set
if MQTT_LWT is not None:
    mqttc.will_set(MQTT_LWT, payload=SCRIPTNAME, qos=0, retain=False)

def get_title(topic):
    ''' Find the "title" (for pushover) or "subject" (for smtp)
        from the topic. '''
    title = None
    for key in conf['titlemap'].keys():
        if paho.topic_matches_sub(key, topic):
            title = conf['titlemap'][key]
            break
    return title

def get_priority(topic):
    ''' Find the "priority" (for pushover)
        from the topic. '''
    priority = None
    for key in conf['prioritymap'].keys():
        if paho.topic_matches_sub(key, topic):
            priority = conf['prioritymap'][key]
            break
    return priority

def get_targets(target, targetkey):
    ''' If no specific target then return ALL targets for 
        this key. '''
    if target is None:
        return conf[targetkey].keys()

    return [target]

def notify_pushover(topic, payload, target):
    ''' Notify a Pushover.net recipient '''
    logging.debug("PUSHOVER -> %s" % (target))

    params = {
            'retry' : 60,
            'expire' : 3600,
        }

    title = get_title(topic)
    if title is not None:
        params['title'] = title

    priority = get_priority(topic)
    if priority is not None:
        params['priority'] = priority

    try:
        userkey = conf['pushover_targets'][target][0]
        appkey = conf['pushover_targets'][target][1]
    except:
        logging.warn("No pushover userkey/appkey configured for target `%s'" % (target))
        return

    try:
        logging.debug("Sending pushover notification to %s [%s]..." % (target, params))
        pushover(message=payload, user=userkey, token=appkey, **params)
        logging.debug("Successfully sent pushover notification")
    except Exception, e:
        logging.warn("Error sending pushover notification to %s [%s]: %s" % (target, params, str(e)))
        return

def notify_smtp(topic, payload, target):
    ''' Notify a recipient by SMTP
        FIXME: I may need to queue this b/c of throughput '''
    logging.debug("SMTP -> %s" % (target))

    try:
        smtp_addresses = conf['smtp_targets'][target]
    except:
        logging.info("No SMTP addresses configured for target `%s'" % (target))
        return

    subject = get_title(topic)
    if subject is None:
        subject = "%s notification" % (SCRIPTNAME)

    server = conf['smtp_config']['server']
    sender = conf['smtp_config']['sender']
    starttls = conf['smtp_config']['starttls']
    username = conf['smtp_config']['username']
    password = conf['smtp_config']['password']

    msg = MIMEText(payload)
    msg['Subject']      = subject
    msg['From']         = sender
    msg['X-Mailer']     = SCRIPTNAME
    # logging.debug(msg.as_string())

    try:
        logging.debug("Sending SMTP notification to %s [%s]..." % (target, smtp_addresses))
        server = smtplib.SMTP(server)
        server.set_debuglevel(0)
        server.ehlo()
        if starttls:
            server.starttls()
        server.ehlo()
        if username:
            server.login(username, password)
        server.sendmail(sender, smtp_addresses, msg.as_string())
        server.quit()
        logging.debug("Successfully sent SMTP notification")
    except Exception, e:
        logging.warn("Error sending notification to SMTP recipient %s [%s]: %s" % (target, smtp_addresses, str(e)))
        return

def connect():
    """
    Connect to the broker
    """
    logging.debug("Attempting connection to MQTT broker %s:%d..." % (MQTT_HOST, MQTT_PORT))
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    try:
        result = mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
        if result == 0:
            mqttc.loop_forever()
        else:
            logging.info("Connection failed with error code %s. Retrying in 10s...", result)
            time.sleep(10)
            connect()
    except Exception, e:
        logging.error("Cannot connect to MQTT broker at %s:%d: %s" % (MQTT_HOST, MQTT_PORT, str(e)))
        sys.exit(2)
         
def disconnect(signum, frame):
    """
    Signal handler to ensure we disconnect cleanly 
    in the event of a SIGTERM or SIGINT.
    """
    logging.debug("Disconnecting from MQTT broker...")
    mqttc.loop_stop()
    mqttc.disconnect()
    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)

def on_connect(mosq, userdata, result_code):
    logging.debug("Connected to MQTT broker, subscribing to topics...")
    for topic in conf['topicmap'].keys():
        logging.debug("Subscribing to %s" % topic)
        mqttc.subscribe(topic, 0)

def on_message(mosq, userdata, msg):
    """
    Message received from the broker
    """
    topic = msg.topic
    payload = str(msg.payload)
    logging.debug("Message received on %s: %s" % (topic, payload))
    
    # Try to find matching settings for this topic
    for key in conf['topicmap'].keys():
        if paho.topic_matches_sub(key, topic):
            targetlist = conf['topicmap'][key]
            logging.debug("Topic [%s] going to %s" % (topic, targetlist))

            for t in targetlist:
                # Each target is either "service" or "service:target"
                # If no target specified then notify ALL targets
                service = t
                target = None

                # Check if this is for a specific target
                if t.find(':') != -1:
                    try:
                        service, target = t.split(':', 2)
                    except:
                        logging.warn("Invalid target %s - should be 'service:target'" % (t))
                        continue

                # PUSHOVER
                if service == 'pushover':
                    for sendto in get_targets(target, 'pushover_targets'):
                        notify_pushover(topic, payload, sendto)

                # SMTP
                elif service == 'smtp':
                    for sendto in get_targets(target, 'smtp_targets'):
                        notify_smtp(topic, payload, sendto)

                else:
                    logging.warn("Unsupported service '%s' in target %s" % (service, t))

    return

def on_disconnect(mosq, userdata, result_code):
    """
    Handle disconnections from the broker
    """
    if result_code == 0:
        logging.info("Clean disconnection")
    else:
        logging.info("Unexpected disconnection! Reconnecting in 5 seconds...")
        logging.debug("Result code: %s", result_code)
        time.sleep(5)
        connect()

# use the signal module to handle signals
signal.signal(signal.SIGTERM, disconnect)
signal.signal(signal.SIGINT, disconnect)
        
# connect to broker and start listening
connect()
