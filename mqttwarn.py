#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
import logging
import signal
import sys
import time
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json
import Queue
import threading
import imp
try:
    import hashlib
    md = hashlib.md5
except ImportError:
    import md5
    md = md5.new
import os
import socket
from ConfigParser import RawConfigParser, NoOptionError
import codecs
import ast
import re
HAVE_TLS = True
try:
    import ssl
except ImportError:
    HAVE_TLS = False
HAVE_JINJA = True
try:
    from jinja2 import Environment, FileSystemLoader
    jenv = Environment(
            loader = FileSystemLoader('templates/', encoding='utf-8'),
            trim_blocks = True)
    jenv.filters['jsonify'] = json.dumps
except ImportError:
    HAVE_JINJA = False

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>, Ben Jones <ben.jones12()gmail.com>'
__copyright__ = 'Copyright 2014 Jan-Piet Mens'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

# script name (without extension) used for config/logfile names
SCRIPTNAME = os.path.splitext(os.path.basename(__file__))[0]

CONFIGFILE = os.getenv(SCRIPTNAME.upper() + 'INI', SCRIPTNAME + '.ini')
LOGFILE    = os.getenv(SCRIPTNAME.upper() + 'LOG', SCRIPTNAME + '.log')

# lwt values - may make these configurable later?
LWTALIVE   = "1"
LWTDEAD    = "0"

class Config(RawConfigParser):

    specials = {
            'TRUE'  : True,
            'FALSE' : False,
            'NONE'  : None,
        }

    def __init__(self, configuration_file):
        RawConfigParser.__init__(self)
        f = codecs.open(configuration_file, 'r', encoding='utf-8')
        self.readfp(f)
        f.close()

        ''' set defaults '''
        self.hostname     = 'localhost'
        self.port         = 1883
        self.username     = None
        self.password     = None
        self.clientid     = SCRIPTNAME
        self.lwt          = 'clients/%s' % SCRIPTNAME
        self.skipretained = False
        self.cleansession = False

        self.logformat    = '%(asctime)-15s %(levelname)-5s [%(module)s] %(message)s'
        self.logfile      = LOGFILE
        self.loglevel     = 'DEBUG'

        self.functions    = None
        self.directory    = '.'
        self.ca_certs     = None
        self.tls_version  = None
        self.certfile     = None
        self.keyfile      = None
        self.tls_insecure = False
        self.tls          = False

        self.__dict__.update(self.config('defaults'))

        if HAVE_TLS == False:
            logging.error("TLS parameters set but no TLS available (SSL)")
            sys.exit(2)

        if self.ca_certs is not None:
            self.tls = True

        if self.tls_version is not None:
            if self.tls_version == 'tlsv1':
                self.tls_version = ssl.PROTOCOL_TLSv1
            if self.tls_version == 'sslv3':
                self.tls_version = ssl.PROTOCOL_SSLv3

        self.loglevelnumber = self.level2number(self.loglevel)

    def level2number(self, level):

        levels = {
            'CRITICAL' : 50,
            'DEBUG' : 10,
            'ERROR' : 40,
            'FATAL' : 50,
            'INFO' : 20,
            'NOTSET' : 0,
            'WARN' : 30,
            'WARNING' : 30,
        }

        return levels.get(level.upper(), levels['DEBUG'])


    def g(self, section, key, default=None):
        try:
            val = self.get(section, key)
            if val.upper() in self.specials:
                return self.specials[val.upper()]
            return ast.literal_eval(val)
        except NoOptionError:
            return default
        except ValueError:   # e.g. %(xxx)s in string
            return val
        except:
            raise
            return val

    def getlist(self, section, key):
        ''' Return a list, fail if it isn't a list '''

        val = None
        try:
            val = self.get(section, key)
            val = [s.strip() for s in val.split(',')]
        except:
            logging.warn("Expecting a list in section `%s', key `%s'" % (section, key))

        return val

    def getdict(self, section, key):
        val = self.g(section, key)

        try:
            return dict(val)
        except:
            return None

    def config(self, section):
        ''' Convert a whole section's options (except the options specified
            explicitly below) into a dict, turning

                [config:mqtt]
                host = 'localhost'
                username = None
                list = [1, 'aaa', 'bbb', 4]

            into

                {u'username': None, u'host': 'localhost', u'list': [1, 'aaa', 'bbb', 4]}

            Cannot use config.items() because I want each value to be
            retrieved with g() as above '''

        d = None
        if self.has_section(section):
            d = dict((key, self.g(section, key))
                for (key) in self.options(section) if key not in ['targets'])
        return d

    def datamap(self, name, topic):
        ''' Attempt to invoke function `name' loaded from the
            `functions' Python package '''

        val = None

        try:
            func = getattr(__import__(cf.functions, fromlist=[name]), name)
            try:
                val = func(topic, srv)  # new version
            except TypeError:
                val = func(topic)       # legacy
        except:
            raise

        return val

    def filter(self, name, topic, payload):
        ''' Attempt to invoke function `name' from the `functions'
            package. Return that function's True/False '''

        rc = False
        try:
            func = getattr(__import__(cf.functions, fromlist=[name]), name)
            rc = func(topic, payload)
        except:
            raise

        return rc

# This class, shamelessly stolen from https://gist.github.com/cypreess/5481681
# The `srv' bits are added for mqttwarn
class PeriodicThread(object):
    """
    Python periodic Thread using Timer with instant cancellation
    """

    def __init__(self, callback=None, period=1, name=None, srv=None, *args, **kwargs):
        self.name = name
        self.srv = srv
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.period = period
        self.stop = False
        self.current_timer = None
        self.schedule_lock = threading.Lock()

    def start(self):
        """
        Mimics Thread standard start method
        """
        self.schedule_timer()

    def run(self):
        """
        By default run callback. Override it if you want to use inheritance
        """
        if self.callback is not None:
            self.callback(srv)

    def _run(self):
        """
        Run desired callback and then reschedule Timer (if thread is not stopped)
        """
        try:
            self.run()
        except Exception, e:
            logging.exception("Exception in running periodic thread")
        finally:
            with self.schedule_lock:
                if not self.stop:
                    self.schedule_timer()

    def schedule_timer(self):
        """
        Schedules next Timer run
        """
        self.current_timer = threading.Timer(self.period, self._run, *self.args, **self.kwargs)
        if self.name:
            self.current_timer.name = self.name
        self.current_timer.start()

    def cancel(self):
        """
        Mimics Timer standard cancel method
        """
        with self.schedule_lock:
            self.stop = True
            if self.current_timer is not None:
                self.current_timer.cancel()

    def join(self):
        """
        Mimics Thread standard join method
        """
        self.current_timer.join()


#    def formatmap(self, name, payload):
#        ''' Attempt to invoke `name' from the `functions' package,
#            and return it's string '''
#
#        val = None
#        try:
#            func = getattr(__import__(cf.functions, fromlist=[name]), name)
#            try:
#                val = func(payload, srv)
#            except TypeError:
#                val = func(payload)
#        except:
#            raise
#
#        return val

try:
    cf = Config(CONFIGFILE)
except Exception, e:
    print "Cannot open configuration at %s: %s" % (CONFIGFILE, str(e))
    sys.exit(2)

LOGLEVEL  = cf.loglevelnumber
LOGFILE   = cf.logfile
LOGFORMAT = cf.logformat

# initialise logging
logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
logging.info("Starting %s" % SCRIPTNAME)
logging.info("INFO MODE")
logging.debug("DEBUG MODE")

# initialise MQTT broker connection
mqttc = paho.Client(cf.clientid, clean_session=cf.cleansession)

# initialise processor queue
q_in = Queue.Queue(maxsize=0)
num_workers = 1
exit_flag = False

ptlist = {}         # List of PeriodicThread() objects

# Class with helper functions which is passed to each plugin
# and its global instantiation
class Service(object):
    def __init__(self, mqttc, logging):
        self.mqttc    = mqttc
        self.logging  = logging
        self.SCRIPTNAME = SCRIPTNAME
srv = Service(None, None)

service_plugins = {}

# http://stackoverflow.com/questions/1305532/
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    def __repr__(self):
        return '<%s>' % str("\n ".join("%s: %s" % (k, repr(v)) for (k, v) in self.__dict__.iteritems()))
    def get(self, key, default=None):
        if key in self.__dict__ and self.__dict__[key] is not None:
            return self.__dict__[key]
        else:
            return default

    def enum(self):
        item = {}
        for (k, v) in self.__dict__.iteritems():
            item[k] = v
        return item

def render_template(filename, data):
    text = None
    if HAVE_JINJA is True:
        template = jenv.get_template(filename)
        text = template.render(data)

    return text

def get_sections():
    sections = []
    for section in cf.sections():
        if section != 'defaults' and section != 'cron' and not section.startswith('config:'):
            if cf.has_option(section, 'targets'):
                sections.append(section)
            else:
                logging.warn("Section `%s' has no targets defined" % section)
    return sections

def get_topic(section):
    if cf.has_option(section, 'topic'):
        return cf.get(section, 'topic')
    return section

def get_qos(section):
    qos = 0
    if cf.has_option(section, 'qos'):
        qos = int(cf.get(section, 'qos'))
    return qos

def get_config(section, name):
    value = None
    if cf.has_option(section, name):
        value = cf.get(section, name)
    return value

def is_filtered(section, topic, payload):
    if cf.has_option(section, 'filter'):
        filterfunc = get_function_name( cf.get(section, 'filter') )
        try:
            return cf.filter(filterfunc, topic, payload)
        except Exception, e:
            logging.warn("Cannot invoke filter function %s defined in %s: %s" % (filterfunc, section, str(e)))
    return False

def get_function_name(s):
    func = None

    if s is not None:
        try:
            valid = re.match('^[\w]+\(\)', s)
            if valid is not None:
                func = re.sub('[()]', '', s)
        except:
            pass
    return func

def get_topic_data(section, topic):
    if cf.has_option(section, 'datamap'):
        name = get_function_name(cf.get(section, 'datamap'))
        try:
            return cf.datamap(name, topic)
        except Exception, e:
            logging.warn("Cannot invoke datamap function %s defined in %s: %s" % (name, section, str(e)))
    return None

class Job(object):
    def __init__(self, prio, service, section, topic, payload, target):
        self.prio       = prio
        self.service    = service
        self.section    = section
        self.topic      = topic
        self.payload    = payload
        self.target     = target

        logging.debug("New `%s:%s' job: %s" % (service, target, topic))
        return
    def __cmp__(self, other):
        return cmp(self.prio, other.prio)

# MQTT broker callbacks
def on_connect(mosq, userdata, result_code):
    """
    Handle connections (or failures) to the broker.
    This is called after the client has received a CONNACK message
    from the broker in response to calling connect().

    The result_code is one of;
    0: Success
    1: Refused - unacceptable protocol version
    2: Refused - identifier rejected
    3: Refused - server unavailable
    4: Refused - bad user name or password (MQTT v3.1 broker only)
    5: Refused - not authorised (MQTT v3.1 broker only)
    """
    if result_code == 0:
        logging.debug("Connected to MQTT broker, subscribing to topics...")

        subscribed = []
        for section in get_sections():
            topic = get_topic(section)
            qos = get_qos(section)

            if topic in subscribed:
                continue

            logging.debug("Subscribing to %s (qos=%d)" % (topic, qos))
            mqttc.subscribe(str(topic), qos)
            subscribed.append(topic)

        mqttc.publish(cf.lwt, LWTALIVE, qos=0, retain=True)

    elif result_code == 1:
        logging.info("Connection refused - unacceptable protocol version")
    elif result_code == 2:
        logging.info("Connection refused - identifier rejected")
    elif result_code == 3:
        logging.info("Connection refused - server unavailable")
    elif result_code == 4:
        logging.info("Connection refused - bad user name or password")
    elif result_code == 5:
        logging.info("Connection refused - not authorised")
    else:
        logging.warning("Connection failed - result code %d" % (result_code))

def on_disconnect(mosq, userdata, result_code):
    """
    Handle disconnections from the broker
    """
    if result_code == 0:
        logging.info("Clean disconnection from broker")
    else:
        logging.info("Broker connection lost. Will attempt to reconnect in 5s...")
        time.sleep(5)

def on_message(mosq, userdata, msg):
    """
    Message received from the broker
    """
    topic = msg.topic
    payload = str(msg.payload)
    logging.debug("Message received on %s: %s" % (topic, payload))

    if msg.retain == 1:
        if cf.skipretained:
            logging.debug("Skipping retained message on %s" % topic)
            return

    # Try to find matching settings for this topic
    for section in get_sections():
        # Get the topic for this section (usually the section name but optionally overridden)
        match_topic = get_topic(section)
        if paho.topic_matches_sub(match_topic, topic):
            logging.debug("Section [%s] matches message on %s. Processing..." % (section, topic))
            # Check for any message filters
            if is_filtered(section, topic, payload):
                logging.debug("Filter in section [%s] has skipped message on %s" % (section, topic))
                continue

            targetlist = cf.getlist(section, 'targets')
            if type(targetlist) != list:
                logging.error("Target definition in section [%s] is incorrect" % section)
                cleanup(0)
                return

            for t in targetlist:
                logging.debug("Message on %s going to %s" % (topic, t))
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

                if not service in service_plugins:
                    logging.error("Invalid configuration: topic %s points to non-existing service %s" % (topic, service))
                    return

                sendtos = None
                if target is None:
                    sendtos = get_service_targets(service)
                else:
                    sendtos = [target]

                for sendto in sendtos:
                    job = Job(1, service, section, topic, payload, sendto)
                    q_in.put(job)
# End of MQTT broker callbacks

def builtin_transform_data(topic, payload):
    ''' Return a dict with initial transformation data which is made
        available to all plugins '''

    tdata = {}
    dt = datetime.now()

    tdata['topic']      = topic
    tdata['payload']    = payload
    tdata['_dtepoch']   = int(time.time())          # 1392628581
    tdata['_dtiso']     = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ") # 2014-02-17T10:38:43.910691Z
    tdata['_dthhmm']    = dt.strftime('%H:%M')      # 10:16
    tdata['_dthhmmss']  = dt.strftime('%H:%M:%S')   # hhmmss=10:16:21

    return tdata

def get_service_config(service):
    config = cf.config('config:' + service)
    if config is None:
        return {}
    return dict(config)

def get_service_targets(service):
    try:
        targets = cf.getdict('config:' + service, 'targets')
        if type(targets) != dict:
            logging.error("No targets for service `%s'" % service)
            cleanup(0)
    except:
        logging.error("No targets for service `%s'" % service)
        cleanup(0)

    if targets is None:
        return {}
    return dict(targets)

def xform(function, orig_value, transform_data):
    ''' Attempt transformation on orig_value.
        1st. function()
        2nd. inline {xxxx}
        '''

    if orig_value is None:
        return None

    res = orig_value

    if function is not None:
        function_name = get_function_name(function)
        if function_name is not None:
            try:
                res = cf.datamap(function_name, transform_data)
                return res
            except Exception, e:
                logging.warn("Cannot invoke %s(): %s" % (function_name, str(e)))

        try:
            res = function.format(**transform_data).encode('utf-8')
        except Exception, e:
            pass

    if type(res) == str:
        res = res.replace("\\n", "\n")
    return res

def processor():
    """
    Queue runner. Pull a job from the queue, find the module in charge
    of handling the service, and invoke the module's plugin to do so.
    """

    while not exit_flag:
        job = q_in.get(15)

        service = job.service
        section = job.section
        target  = job.target

        logging.debug("Processor is handling: `%s' for %s" % (service, target))

        item = {
            'service'       : service,
            'section'       : section,
            'target'        : target,
            'config'        : get_service_config(service),
            'addrs'         : get_service_targets(service)[target],
            'topic'         : job.topic,
            'payload'       : job.payload,
            'data'          : None,
            'title'         : None,
            'image'         : None,
            'message'       : None,
            'priority'      : None
        }

        transform_data = builtin_transform_data(job.topic, job.payload)

        topic_data = get_topic_data(job.section, job.topic)
        if topic_data is not None and type(topic_data) == dict:
            transform_data = dict(transform_data.items() + topic_data.items())

        # Attempt to decode the payload from JSON. If it's possible, add
        # the JSON keys into item to pass to the plugin, and create the
        # outgoing (i.e. transformed) message.
        try:
            payload_data = json.loads(job.payload)
            transform_data = dict(transform_data.items() + payload_data.items())
        except:
            pass

        item['data'] = dict(transform_data.items())

        item['title'] = xform(get_config(section, 'title'), SCRIPTNAME, transform_data)
        item['image'] = xform(get_config(section, 'image'), '', transform_data)
        item['message'] = xform(get_config(section, 'format'), job.payload, transform_data)
        item['priority'] = int(xform(get_config(section, 'priority'), 0, transform_data))
        item['callback'] = xform(get_config(section, 'callback'), SCRIPTNAME, transform_data)

        if HAVE_JINJA is True:
            template = get_config(section, 'template')
            if template is not None:
                try:
                    text = render_template(template, transform_data)
                    if text is not None:
                        item['message'] = text
                except Exception, e:
                    logging.warn("Cannot render `%s' template: %s" % (template, str(e)))

        if item.get('message') is not None and len(item.get('message')) > 0:
            st = Struct(**item)
            notified = False
            try:
                module = service_plugins[service]['module']
                notified = module.plugin(srv, st)
            except Exception, e:
                logging.error("Cannot invoke service for `%s': %s" % (service, str(e)))

            if not notified:
                logging.warn("Notification of %s for `%s' FAILED" % (service, item.get('topic')))
        else:
            logging.warn("Notification of %s for `%s' suppressed: text is empty" % (service, item.get('topic')))

        q_in.task_done()

    logging.debug("Thread exiting...")

# http://code.davidjanes.com/blog/2008/11/27/how-to-dynamically-load-python-code/
def load_module(path):
    try:
        fp = open(path, 'rb')
        return imp.load_source(md(path).hexdigest(), path, fp)
    finally:
        try:
            fp.close()
        except:
            pass

def load_services(services):
    for service in services:
        modulefile = 'services/%s.py' % service

        service_plugins[service] = {}

        try:
            service_plugins[service]['module'] = load_module(modulefile)
            logging.debug("Service %s loaded" % (service))
        except Exception, e:
            logging.error("Can't load %s service (%s): %s" % (service, modulefile, str(e)))
            sys.exit(1)

        try:
            service_config = cf.config('config:' + service)
        except Exception, e:
            logging.error("Service `%s' has no config section: %s" % (service, str(e)))
            sys.exit(1)

        service_plugins[service]['config'] = service_config

def connect():
    """
    Load service plugins, connect to the broker, launch daemon threads and listen forever
    """

    try:
        services = cf.getlist('defaults', 'launch')
    except:
        logging.error("No services configured. Aborting")
        sys.exit(2)

    try:
        os.chdir(cf.directory)
    except Exception, e:
        logging.error("Cannot chdir to %s: %s" % (cf.directory, str(e)))
        sys.exit(2)

    load_services(services)

    srv.mqttc = mqttc
    srv.logging = logging

    logging.debug("Attempting connection to MQTT broker %s:%d..." % (cf.hostname, int(cf.port)))
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    # check for authentication
    if cf.username:
        mqttc.username_pw_set(cf.username, cf.password)

    # set the lwt before connecting
    logging.debug("Setting LWT to %s..." % (cf.lwt))
    mqttc.will_set(cf.lwt, payload=LWTDEAD, qos=0, retain=True)

    # Delays will be: 3, 6, 12, 24, 30, 30, ...
    # mqttc.reconnect_delay_set(delay=3, delay_max=30, exponential_backoff=True)

    if cf.tls == True:
        mqttc.tls_set(cf.ca_certs, cf.certfile, cf.keyfile, tls_version=cf.tls_version, ciphers=None)

    if cf.tls_insecure:
        mqttc.tls_insecure_set(True)

    try:
        mqttc.connect(cf.hostname, int(cf.port), 60)
    except Exception, e:
        logging.error("Cannot connect to MQTT broker at %s:%d: %s" % (cf.hostname, int(cf.port), str(e)))
        sys.exit(2)

    # Launch worker threads to operate on queue
    for i in range(num_workers):
        t = threading.Thread(target=processor)
        t.daemon = True
        t.start()

    # If the config file has a [cron] section, the key names therein are
    # functions from 'myfuncs.py' which should be invoked periodically.
    # The key's value (must be numeric!) is the period in seconds.

    if cf.has_section('cron'):
        for name, val in cf.items('cron'):
            try:
                func = getattr(__import__(cf.functions, fromlist=[name]), name)
                interval = float(val)
                ptlist[name] = PeriodicThread(func, interval, srv=srv)
                ptlist[name].start()
            except AttributeError:
                logging.error("[cron] section has function [%s] specified, but that's not defined" % name)
                continue



    while True:
        try:
            mqttc.loop_forever()
        except socket.error:
            logging.info("MQTT server disconnected; sleeping")
            time.sleep(5)
        except:
            # FIXME: add logging with trace
            raise

def cleanup(signum=None, frame=None):
    """
    Signal handler to ensure we disconnect cleanly
    in the event of a SIGTERM or SIGINT.
    """

    global exit_flag

    exit_flag = True

    for ptname in ptlist:
        logging.debug("Cancel %s timer" % ptname)
        ptlist[ptname].cancel()

    logging.debug("Disconnecting from MQTT broker...")
    mqttc.publish(cf.lwt, LWTDEAD, qos=0, retain=True)
    mqttc.loop_stop()
    mqttc.disconnect()

    logging.info("Waiting for queue to drain")
    q_in.join()

    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)

if __name__ == '__main__':

    # use the signal module to handle signals
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    # connect to broker and start listening
    connect()
