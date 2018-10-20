#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import paho.mqtt.client as paho   # pip install paho-mqtt
import imp
import logging
import signal
import sys
import time
import types
import string
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
        self.protocol     = 3

        self.logformat    = '%(asctime)-15s %(levelname)-5s [%(module)s] %(message)s'
        self.logfile      = LOGFILE
        self.loglevel     = 'DEBUG'

        self.functions    = None
        self.num_workers  = 1

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
            if self.tls_version == 'tlsv1_2':
                self.tls_version = ssl.PROTOCOL_TLSv1_2
            if self.tls_version == 'tlsv1_1':
                self.tls_version = ssl.PROTOCOL_TLSv1_1
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
        except SyntaxError:  # If not python value, e.g. list of targets coma separated
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
        except Exception, e:
            logging.warn("Expecting a list in section `%s', key `%s' (%s)" % (section, key, str(e)))

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
                for (key) in self.options(section) if key not in ['targets', 'module'])
        return d

    def datamap(self, name, topic):
        ''' Attempt to invoke function `name' loaded from the
            `functions' Python package '''

        val = None

        try:
            func = load_function(name)
            try:
                val = func(topic, srv)  # new version
            except TypeError:
                val = func(topic)       # legacy
        except:
            raise

        return val

    def alldata(self, name, topic, data):
        ''' Attempt to invoke function `name' loaded from the
            `functions' Python package '''

        val = None

        try:
            func = load_function(name)
            val = func(topic, data, srv)
        except:
            raise

        return val

    def topic_target_list(self, name, topic, data):
        """
        Attempt to invoke function `name' loaded from the
        `functions' Python package for computing dynamic
        topic subscription targets.
        Pass MQTT topic and transformation data.
        """

        val = None

        try:
            func = load_function(name)
            val = func(topic=topic, data=data, srv=srv)
        except:
            raise

        return val

    def filter(self, name, topic, payload, section=None):
        ''' Attempt to invoke function `name' from the `functions'
            package. Return that function's True/False '''

        rc = False
        try:
            func = load_function(name)
            try:
                rc = func(topic, payload, section, srv)  # new version
            except TypeError:
                rc = func(topic, payload)                # legacy signature
        except:
            raise

        return rc

# This class, shamelessly stolen from https://gist.github.com/cypreess/5481681
# The `srv' bits are added for mqttwarn
class PeriodicThread(object):
    """
    Python periodic Thread using Timer with instant cancellation
    """

    def __init__(self, callback=None, period=1, name=None, srv=None, now=False, *args, **kwargs):
        self.name = name
        self.srv = srv
        self.now = now
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

        # Schedule periodic task to run right now
        if self.now == True:
            self.run()

        # Schedule periodic task with designated interval
        self.schedule_timer()

    def run(self):
        """
        By default run callback. Override it if you want to use inheritance
        """
        if self.callback is not None:
            self.callback(srv, *self.args, **self.kwargs)

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
        self.current_timer = threading.Timer(self.period, self._run)
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

try:
    cf = Config(CONFIGFILE)
except Exception, e:
    print "Cannot open configuration at %s: %s" % (CONFIGFILE, str(e))
    shutil.copyfile('mqttwarn.ini.sample', CONFIGFILE + '.sample')
    print "\nA sample configuration file has been created at %s. Please rename to mqttwarn.ini and edit as appropriate." % (CONFIGFILE + '.sample')
    sys.exit(2)

LOGLEVEL  = cf.loglevelnumber
LOGFILE   = cf.logfile
LOGFORMAT = cf.logformat

# initialise logging
# Send log messages to sys.stderr by configuring "logfile = stream://sys.stderr"
if LOGFILE.startswith('stream://'):
    LOGFILE = LOGFILE.replace('stream://', '')
    logging.basicConfig(stream=eval(LOGFILE), level=LOGLEVEL, format=LOGFORMAT)
# Send log messages to file by configuring "logfile = 'mqttwarn.log'"
else:
    logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
logging.info("Starting %s" % SCRIPTNAME)
logging.info("Log level is %s" % logging.getLevelName(LOGLEVEL))

# initialise MQTT broker connection
mqttc = paho.Client(cf.clientid, clean_session=cf.cleansession, protocol=cf.protocol)

# initialise processor queue
q_in = Queue.Queue(maxsize=0)
exit_flag = False

ptlist = {}         # List of PeriodicThread() objects

# Class with helper functions which is passed to each plugin
# and its global instantiation
class Service(object):
    def __init__(self, mqttc, logging):

        # Reference to MQTT client object
        self.mqttc    = mqttc

        # Reference to all mqttwarn globals, for using its machinery from plugins
        self.mwcore   = globals()

        # Reference to logging object
        self.logging  = logging

        # Name of self ("mqttwarn", mostly)
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

class Formatter(string.Formatter):
    """
    A custom string formatter. See also:
    - https://docs.python.org/2/library/string.html#format-string-syntax
    - https://docs.python.org/2/library/string.html#custom-string-formatting
    """

    def convert_field(self, value, conversion):
        """
        The conversion field causes a type coercion before formatting.
        By default, two conversion flags are supported: '!s' which calls
        str() on the value, and '!r' which calls repr().

        This also adds the '!j' conversion flag, which serializes the
        value to JSON format.

        See also https://github.com/jpmens/mqttwarn/issues/146.
        """
        if conversion == 'j':
            value = json.dumps(value)
        return value

def render_template(filename, data):
    text = None
    if HAVE_JINJA is True:
        template = jenv.get_template(filename)
        text = template.render(data)

    return text

def get_sections():
    sections = []
    for section in cf.sections():
        if section == 'defaults':
            continue
        if section == 'cron':
            continue
        if section == 'failover':
            continue
        if section.startswith('config:'):
            continue
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

def asbool(obj):
    """
    Shamelessly stolen from beaker.converters
    # (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
    # Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
    """
    if isinstance(obj, basestring):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

def parse_cron_options(argstring):
    """
    Parse periodic task options.
    Obtains configuration value, returns dictionary.

    Example::

        my_periodic_task = 60; now=true

    """
    parts = argstring.split(';')
    options = {'interval': float(parts[0].strip())}
    for part in parts[1:]:
        name, value = part.split('=')
        options[name.strip()] = value.strip()
    return options

def is_filtered(section, topic, payload):
    if cf.has_option(section, 'filter'):
        filterfunc = get_function_name( cf.get(section, 'filter') )
        try:
            return cf.filter(filterfunc, topic, payload, section)
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

def get_all_data(section, topic, data):
    if cf.has_option(section, 'alldata'):
        name = get_function_name(cf.get(section, 'alldata'))
        try:
            return cf.alldata(name, topic, data)
        except Exception, e:
            logging.warn("Cannot invoke alldata function %s defined in %s: %s" % (name, section, str(e)))
    return None

def get_topic_targets(section, topic, data):
    """
    Topic targets function invoker.
    """
    if cf.has_option(section, 'targets'):
        name = get_function_name(cf.get(section, 'targets'))
        try:
            return cf.topic_target_list(name, topic, data)
        except Exception as ex:
            error = repr(ex)
            logging.warn('Error invoking topic targets function "{name}" ' \
                         'defined in section "{section}": {error}'.format(**locals()))
    return None

class Job(object):
    def __init__(self, prio, service, section, topic, payload, data, target):
        self.prio       = prio
        self.service    = service
        self.section    = section
        self.topic      = topic
        self.payload    = payload       # raw payload
        self.data       = data          # decoded payload
        self.target     = target

        logging.debug("New `%s:%s' job: %s" % (service, target, topic))
        return
    def __cmp__(self, other):
        return cmp(self.prio, other.prio)

# MQTT broker callbacks
def on_connect(mosq, userdata, flags, result_code):
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
        if not cf.cleansession:
            logging.debug("Cleansession==False; previous subscriptions for clientid %s remain active on broker" % cf.clientid)

        subscribed = []
        for section in get_sections():
            topic = get_topic(section)
            qos = get_qos(section)

            if topic in subscribed:
                continue

            logging.debug("Subscribing to %s (qos=%d)" % (topic, qos))
            mqttc.subscribe(str(topic), qos)
            subscribed.append(topic)

        if cf.lwt is not None:
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
        send_failover("brokerdisconnected", "Broker connection lost. Will attempt to reconnect in 5s...")
        time.sleep(5)

def on_message(mosq, userdata, msg):
    """
    Message received from the broker
    """
    topic = msg.topic
    try:
        payload = msg.payload.decode('utf-8')
    except UnicodeEncodeError:
        payload = msg.payload
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
            # Send the message to any targets specified
            send_to_targets(section, topic, payload)
# End of MQTT broker callbacks

def send_failover(reason, message):
    # Make sure we dump this event to the log
    logging.warn(message)
    # Attempt to send the message to our failover targets
    send_to_targets('failover', reason, message)

def send_to_targets(section, topic, payload):
    if cf.has_section(section) == False:
        logging.warn("Section [%s] does not exist in your INI file, skipping message on %s" % (section, topic))
        return

    # decode raw payload into transformation data
    data = decode_payload(section, topic, payload)

    dispatcher_dict = cf.getdict(section, 'targets')
    function_name = get_function_name(get_config(section, 'targets'))

    if function_name is not None:
        targetlist = get_topic_targets(section, topic, data)
        targetlist_type = type(targetlist)
        if targetlist_type is not types.ListType:
            logging.error('Topic target definition by function "{function_name}" ' \
                          'in section "{section}" is empty or incorrect. ' \
                          'targetlist={targetlist}, type={targetlist_type}'.format(**locals()))
            return

    elif type(dispatcher_dict) == dict:
        def get_key(item):
            # precede a key with the number of topic levels and then use reverse alphabetic sort order
            # '+' is after '#' in ascii table
            # caveat: for instance space is allowed in topic name but will be less specific than '+', '#'
            # so replace '#' with first ascii character and '+' with second ascii character
            # http://public.dhe.ibm.com/software/dw/webservices/ws-mqtt/mqtt-v3r1.html#appendix-a

            # item[0] represents topic. replace wildcard characters to ensure the right order
            modified_topic = item[0].replace('#', chr(0x01)).replace('+', chr(0x02))
            levels = len(item[0].split('/'))
            # concatenate levels with leading zeros and modified topic and return as a key
            return "{:03d}{}".format(levels, modified_topic)

        # produce a sorted list of topic/targets with longest and more specific first
        sorted_dispatcher = sorted(dispatcher_dict.items(), key=get_key, reverse=True)
        for match_topic, targets in sorted_dispatcher:
            if paho.topic_matches_sub(match_topic, topic):
                # hocus pocus, let targets become a list
                targetlist = targets if type(targets) == list else [targets]
                logging.debug("Most specific match %s dispatched to %s" % (match_topic, targets))
                # first most specific topic matches then stops processing
                break
        else:
            # Not found then no action. This could be configured intentionally.
            logging.debug("Dispatcher definition does not contain matching topic/target pair in section [%s]" % section)
            return
    else:
        targetlist = cf.getlist(section, 'targets')
        if type(targetlist) != list:
            # if targets is neither dict nor list
            logging.error("Target definition in section [%s] is incorrect" % section)
            cleanup(0)
            return

    # interpolate transformation data values into topic targets
    # be graceful if interpolation fails, but log a meaningful message
    targetlist_resolved = []
    for target in targetlist:
        try:
            target = target.format(**data)
            targetlist_resolved.append(target)
        except Exception as ex:
            error = repr(ex)
            logging.error('Cannot interpolate transformation data into topic target "{target}": {error}. ' \
                          'section={section}, topic={topic}, payload={payload}, data={data}'.format(**locals()))
    targetlist = targetlist_resolved

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

        # skip targets with invalid services
        if not service in service_plugins:
            logging.error("Invalid configuration: topic %s points to non-existing service %s" % (topic, service))
            continue

        sendtos = None
        if target is None:
            sendtos = get_service_targets(service)
        else:
            sendtos = [target]

        for sendto in sendtos:
            job = Job(1, service, section, topic, payload, data, sendto)
            q_in.put(job)

def builtin_transform_data(topic, payload):
    ''' Return a dict with initial transformation data which is made
        available to all plugins '''

    tdata = {}
    dt = datetime.now()

    tdata['topic']      = topic
    tdata['payload']    = payload
    tdata['_dtepoch']   = int(time.time())          # 1392628581
    tdata['_dtiso']     = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ") # 2014-02-17T10:38:43.910691Z
    tdata['_ltiso']     = datetime.now().isoformat() #local time in iso format
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
            res = Formatter().format(function, **transform_data).encode('utf-8')
        except Exception, e:
            logging.warning("Cannot format message: %s" % e)

    if type(res) == str:
        res = res.replace("\\n", "\n")
    return res

# http://code.activestate.com/recipes/473878-timeout-function-using-threading/
def timeout(func, args=(), kwargs={}, timeout_secs=10, default=False):
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_secs)
    if it.isAlive():
        return default
    else:
        return it.result

def decode_payload(section, topic, payload):
    """
    Decode message payload through transformation machinery.
    """

    transform_data = builtin_transform_data(topic, payload)

    topic_data = get_topic_data(section, topic)
    if topic_data is not None and type(topic_data) == dict:
        transform_data = dict(transform_data.items() + topic_data.items())

    # The dict returned is completely merged into transformation data
    # The difference between this and `get_topic_data()' is that this
    # function obtains the topic string as well as the payload and any
    # existing transformation data, and it can do 'things' with all.
    # This is the way it should originally have been, but I can no
    # longer fix the original ... (legacy)

    all_data = get_all_data(section, topic, transform_data)
    if all_data is not None and type(all_data) == dict:
        transform_data = dict(transform_data.items() + all_data.items())

    # Attempt to decode the payload from JSON. If it's possible, add
    # the JSON keys into item to pass to the plugin, and create the
    # outgoing (i.e. transformed) message.
    try:
        payload = payload.rstrip("\0")
        payload_data = json.loads(payload)
        transform_data = dict(transform_data.items() + payload_data.items())
    except Exception as ex:
        logging.debug(u"Cannot decode JSON object, payload={payload}: {ex}".format(**locals()))

    return transform_data

def processor(worker_id=None):
    """
    Queue runner. Pull a job from the queue, find the module in charge
    of handling the service, and invoke the module's plugin to do so.
    """

    while not exit_flag:
        logging.debug('Job queue has %s items to process' % q_in.qsize())
        job = q_in.get()

        service = job.service
        section = job.section
        target  = job.target
        topic   = job.topic

        logging.debug("Processor #%s is handling: `%s' for %s" % (worker_id, service, target))

        # sanity checks
        # if service configuration or targets can not be obtained successfully,
        # log a sensible error message, fail the job and carry on with the next job
        try:
            service_config  = get_service_config(service)
            service_targets = get_service_targets(service)

            if target not in service_targets:
                error_message = "Invalid configuration: topic {topic} points to " \
                                "non-existing target {target} in service {service}".format(**locals())
                raise KeyError(error_message)

        except Exception, e:
            logging.error("Cannot handle service=%s, target=%s: %s" % (service, target, repr(e)))
            q_in.task_done()
            continue

        item = {
            'service'       : service,
            'section'       : section,
            'target'        : target,
            'config'        : service_config,
            'addrs'         : service_targets[target],
            'topic'         : topic,
            'payload'       : job.payload,
            'data'          : None,
            'title'         : None,
            'image'         : None,
            'message'       : None,
            'priority'      : None
        }

        transform_data = job.data
        item['data'] = dict(transform_data.items())

        item['title'] = xform(get_config(section, 'title'), SCRIPTNAME, transform_data)
        item['image'] = xform(get_config(section, 'image'), '', transform_data)
        item['message'] = xform(get_config(section, 'format'), job.payload, transform_data)

        try:
            item['priority'] = int(xform(get_config(section, 'priority'), 0, transform_data))
        except Exception, e:
            item['priority'] = 0
            logging.warn("Failed to determine the priority, defaulting to zero: %s" % (str(e)))

        if HAVE_JINJA is False and get_config(section, 'template'):
            logging.warn("Templating not possible because Jinja2 is not installed")

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
                # fire the plugin in a separate thread and kill it if it doesn't return in 10s 
                module = service_plugins[service]['module']
                notified = timeout(module.plugin, (srv, st))
            except Exception, e:
                logging.error("Cannot invoke service for `%s': %s" % (service, str(e)))

            if not notified:
                logging.warn("Notification of %s for `%s' FAILED or TIMED OUT" % (service, item.get('topic')))
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
        service_plugins[service] = {}

        service_config = cf.config('config:' + service)
        if service_config is None:
            logging.error("Service `%s' has no config section" % service)
            sys.exit(1)

        service_plugins[service]['config'] = service_config

        module = cf.g('config:' + service, 'module', service)
        modulefile = 'services/%s.py' % module

        try:
            service_plugins[service]['module'] = load_module(modulefile)
            logging.debug("Service %s loaded" % (service))
        except Exception, e:
            logging.error("Can't load %s service (%s): %s" % (service, modulefile, str(e)))
            sys.exit(1)

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
    if cf.lwt is not None:
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
    logging.info('Starting %s worker threads' % cf.num_workers)
    for i in range(cf.num_workers):
        t = threading.Thread(target=processor, kwargs={'worker_id': i})
        t.daemon = True
        t.start()

    # If the config file has a [cron] section, the key names therein are
    # functions from 'myfuncs.py' which should be invoked periodically.
    # The key's value (must be numeric!) is the period in seconds.

    if cf.has_section('cron'):
        for name, val in cf.items('cron'):
            try:
                func = load_function(name)
                cron_options = parse_cron_options(val)
                interval = cron_options['interval']
                logging.debug('Scheduling function "{name}" as periodic task ' \
                              'to run each {interval} seconds via [cron] section'.format(name=name, interval=interval))
                ptlist[name] = PeriodicThread(callback=func, period=interval, name=name, srv=srv, now=asbool(cron_options.get('now')))
                ptlist[name].start()
            except AttributeError:
                logging.error("[cron] section has function [%s] specified, but that's not defined" % name)
                continue

    while not exit_flag:
        reconnect_interval = 5

        try:
            mqttc.loop_forever()
        except socket.error:
            pass
        except:
            # FIXME: add logging with trace
            raise

        if not exit_flag:
            logging.warning("MQTT server disconnected, trying to reconnect each %s seconds" % reconnect_interval)
            time.sleep(reconnect_interval)

def load_function(function):
    mod_inst = None

    functions_path = cf.functions
    mod_name,file_ext = os.path.splitext(os.path.split(functions_path)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, functions_path)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, functions_path)

    if hasattr(py_mod, function):
        mod_inst = getattr(py_mod, function)

    return mod_inst

def cleanup(signum=None, frame=None):
    """
    Signal handler to ensure we disconnect cleanly
    in the event of a SIGTERM or SIGINT.
    """
    for ptname in ptlist:
        logging.debug("Cancel %s timer" % ptname)
        ptlist[ptname].cancel()

    logging.debug("Disconnecting from MQTT broker...")
    if cf.lwt is not None:
        mqttc.publish(cf.lwt, LWTDEAD, qos=0, retain=True)
    mqttc.loop_stop()
    mqttc.disconnect()

    logging.info("Waiting for queue to drain")
    q_in.join()

    # Send exit signal to subsystems _after_ queue was drained
    global exit_flag
    exit_flag = True

    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)

if __name__ == '__main__':

    # use the signal module to handle signals
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    # connect to broker and start listening
    connect()
