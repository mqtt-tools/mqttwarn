# -*- coding: utf-8 -*-
# (c) 2014-2023 The mqttwarn developers
try:
    from importlib.resources import files as resource_files  # type: ignore[attr-defined]
except ImportError:
    from importlib_resources import files as resource_files  # type: ignore[no-redef]

import logging
import os
import socket
import sys
import threading
import time
import typing as t
from builtins import chr, str
from datetime import datetime
from queue import Queue

import paho.mqtt.client as paho
from paho.mqtt.client import Client as MqttClient
from paho.mqtt.client import MQTTMessage

import mqttwarn.configuration
from mqttwarn.context import FunctionInvoker, RuntimeContext
from mqttwarn.cron import PeriodicThread
from mqttwarn.model import Job, Service, StatusInformation, Struct, TdataType
from mqttwarn.util import (
    Formatter,
    asbool,
    load_function,
    load_module_by_name,
    load_module_from_file,
    parse_cron_options,
    sanitize_function_name,
    timeout,
    truncate,
)

try:
    import json
except ImportError:  # pragma: nocover
    import simplejson as json  # type: ignore


HAVE_JINJA = True
try:
    from jinja2 import Environment, FileSystemLoader

    jenv = Environment(loader=FileSystemLoader("templates/", encoding="utf-8"), trim_blocks=True)
    jenv.filters["jsonify"] = json.dumps
except ImportError:
    HAVE_JINJA = False


logger = logging.getLogger(__name__)

# Name of calling program
SCRIPTNAME = "mqttwarn"

# Global runtime context object
context: RuntimeContext
context = None  # type: ignore[assignment]

# Global configuration object
cf: mqttwarn.configuration.Config
cf = None  # type: ignore[assignment]

# Global handle to MQTT client
mqttc: paho.Client
mqttc = None  # type: ignore[assignment]

# Initialize processor queue
q_in: Queue = Queue(maxsize=0)
exit_flag = False

# Instances of PeriodicThread objects
ptlist: t.Dict[str, PeriodicThread] = {}

# Instances of loaded service plugins
service_plugins: t.Dict[str, t.Dict[str, t.Any]] = dict()


def make_service(mqttc: paho.Client = None, name: t.Optional[str] = None) -> Service:
    """
    Service object factory.
    Prepare service object for plugin.
    Inject appropriate MQTT client and logger objects.

    :param mqttc: Instance of PAHO MQTT client object.
    :param name:  Name used for obtaining a logger instance.
    :return:      Service object ready for being passed to plugin instance.
    """
    name = name or "unknown"
    logger = logging.getLogger(name)
    service = Service(mqttc=mqttc, logger=logger, mwcore=globals(), program=SCRIPTNAME)
    return service


def render_template(filename: str, data: TdataType) -> t.Optional[str]:
    text = None
    if HAVE_JINJA is True:
        template = jenv.get_template(filename)
        text = template.render(data)

    return text


# MQTT broker callbacks
def on_connect(mosq: MqttClient, userdata: t.Dict[str, str], flags: t.Dict[str, str], result_code: int):
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
        logger.debug("Connected to MQTT broker, subscribing to topics")
        if not cf.cleansession:
            logger.debug(
                "Cleansession==False; previous subscriptions for clientid %s remain active on broker" % cf.clientid
            )

        subscribed = []
        for section in context.get_sections():
            topic = context.get_topic(section)
            qos = context.get_qos(section)

            if topic in subscribed:
                continue

            logger.debug("Subscribing to %s (qos=%d)" % (topic, qos))
            mqttc.subscribe(topic, qos)
            subscribed.append(topic)

        if cf.lwt is not None:
            mqttc.publish(cf.lwt, cf.lwt_alive, qos=0, retain=True)

    elif result_code == 1:
        logger.error("Connection refused - unacceptable protocol version")
    elif result_code == 2:
        logger.error("Connection refused - identifier rejected")
    elif result_code == 3:
        logger.error("Connection refused - server unavailable")
    elif result_code == 4:
        logger.error("Connection refused - bad user name or password")
    elif result_code == 5:
        logger.error("Connection refused - not authorised")
    else:
        logger.error("Connection failed - result code %d" % (result_code))


def on_disconnect(mosq: MqttClient, userdata: t.Dict[str, str], result_code: int):
    """
    Handle disconnections from the broker
    """
    if result_code == 0:
        logger.info("Clean disconnection from broker")
    else:
        send_failover("brokerdisconnected", b"Broker connection lost. Will attempt to reconnect in 5s")
        # TODO: Review this.
        time.sleep(5)


def on_message(mosq: MqttClient, userdata: t.Dict[str, str], msg: MQTTMessage):
    """
    Dispatch message received from the MQTT broker to mqttwarn's handler machinery.
    """
    try:
        return on_message_handler(mosq, userdata, msg)
    except:
        logger.exception("Receiving and decoding MQTT message failed")


def on_message_handler(mosq: MqttClient, userdata: t.Dict[str, str], msg: MQTTMessage):
    """
    Message received from the broker
    """

    topic = msg.topic
    payload = msg.payload
    logger.debug(f"Message received on {topic}: {truncate(payload)}")

    if msg.retain == 1:
        if cf.skipretained:
            logger.debug("Skipping retained message on %s" % topic)
            return

    # Try to find matching settings for this topic
    for section in context.get_sections():
        # Get the topic for this section (usually the section name but optionally overridden)
        match_topic = context.get_topic(section)
        if paho.topic_matches_sub(match_topic, topic):
            logger.debug("Section [%s] matches message on %s, processing it" % (section, topic))
            # Check for any message filters
            if context.is_filtered(section, topic, payload):
                logger.log(
                    cf.filteredmessagesloglevelnumber,
                    "Filter in section [%s] has skipped message on %s" % (section, topic),
                )
                continue
            # Send the message to any targets specified
            send_to_targets(section, topic, payload)


# End of MQTT broker callbacks


def send_failover(reason: str, message: t.AnyStr):
    # Make sure we dump this event to the log
    logger.warning(message)
    # Attempt to send the message to our failover targets
    send_to_targets("failover", reason, message)


def send_to_targets(section: str, topic: str, payload: t.AnyStr):
    if cf.has_section(section) is False:
        logger.warning(
            "Section [%s] does not exist in your INI file, skipping message on topic '%s'" % (section, topic)
        )
        return

    # decode raw payload into transformation data
    data = decode_payload(section, topic, payload)

    # Probe if it's a function name.
    function_name = None
    try:
        function_name = sanitize_function_name(context.get_config(section, "targets"))
    except:
        pass
    dispatcher_dict = cf.getdict(section, "targets")

    # `targets` is a function symbol.
    if function_name is not None:
        targetlist = context.get_topic_targets(section, topic, data)

        # Make sure the function returned a target _list_ of elements.
        if not isinstance(targetlist, list):
            targetlist_type = type(targetlist)
            logger.error(
                'Topic target definition by function "{function_name}" '
                'in section "{section}" is empty or incorrect. Should be a list. '
                "targetlist={targetlist}, type={targetlist_type}".format(**locals())
            )
            return

    # `targets` is a dictionary.
    elif isinstance(dispatcher_dict, dict) and dispatcher_dict:

        def get_key(item):
            # precede a key with the number of topic levels and then use reverse alphabetic sort order
            # '+' is after '#' in ascii table
            # caveat: for instance space is allowed in topic name but will be less specific than '+', '#'
            # so replace '#' with first ascii character and '+' with second ascii character
            # http://public.dhe.ibm.com/software/dw/webservices/ws-mqtt/mqtt-v3r1.html#appendix-a

            # item[0] represents topic. replace wildcard characters to ensure the right order
            modified_topic = item[0].replace("#", chr(0x01)).replace("+", chr(0x02))
            levels = len(item[0].split("/"))
            # concatenate levels with leading zeros and modified topic and return as a key
            return "{:03d}{}".format(levels, modified_topic)

        # produce a sorted list of topic/targets with longest and more specific first
        sorted_dispatcher = sorted(list(dispatcher_dict.items()), key=get_key, reverse=True)
        for match_topic, targets in sorted_dispatcher:
            if paho.topic_matches_sub(match_topic, topic):
                # hocus pocus, let targets become a list
                targetlist = targets if isinstance(targets, list) else [targets]
                logger.debug("Most specific match %s dispatched to %s" % (match_topic, targets))
                # first most specific topic matches then stops processing
                break
        else:
            # Not found then no action. This could be configured intentionally.
            logger.debug("Dispatcher definition does not contain matching topic/target pair in section [%s]" % section)
            return

    else:
        targetlist = cf.getlist(section, "targets")

        # Make sure targets are actually a _list_ of elements.
        # TODO: Not tested yet. How can this code be reached?
        if targetlist is None:
            logger.error(
                f'Topic target definition in section "{section}" is empty or incorrect. Should be a list. '
                "targetlist={targetlist}".format(**locals())
            )
            return

    # Interpolate transformation data values into topic targets.
    # Be graceful if interpolation fails, but log a meaningful message.
    targetlist_resolved = []
    for target in targetlist:
        try:
            target = target.format(**data)
            targetlist_resolved.append(target)
        except Exception as ex:
            error = repr(ex)
            logger.error(
                f"Interpolating transformation data into topic target '{target}' failed. Reason: {error}. "
                f"section={section}, topic={topic}, payload={truncate(payload)}, data=%s",
                data,
            )
    targetlist = targetlist_resolved

    for item in targetlist:
        logger.debug("Message on %s going to %s" % (topic, item))
        # Each target is either "service" or "service:target"
        # If no target specified then notify ALL targets
        service = item
        target = None

        # Check if this is for a specific target
        if item.find(":") != -1:
            try:
                service, target = item.split(":", 2)
            except:
                logger.error(f"Invalid topic target: {item}. Should be 'service:target'.")
                continue

        # Skip targets with invalid services.
        if service not in service_plugins:
            logger.error("Invalid configuration: Topic '%s' points to non-existing service '%s'" % (topic, service))
            continue

        service_config = context.get_service_config(service)
        payload_out: t.Union[str, bytes]
        if asbool(service_config.get("decode_utf8", True)) and isinstance(payload, bytes):
            payload_out = payload.decode("utf-8")
        else:
            payload_out = payload

        sendtos = None
        if target is None:
            sendtos = context.get_service_targets(service)
        else:
            sendtos = [target]

        for sendto in sendtos:
            logger.debug("New `%s:%s' job: %s" % (service, sendto, topic))
            job = Job(1, service, section, topic, payload_out, data, sendto)
            q_in.put(job)


def builtin_transform_data(topic: str, payload: t.Union[str, bytes]) -> TdataType:
    """Return a dict with initial transformation data which is made
    available to all plugins"""

    tdata: TdataType = {}
    dt = datetime.now()

    tdata["topic"] = topic
    tdata["payload"] = payload
    tdata["_dtepoch"] = int(time.time())  # 1392628581
    tdata["_dtiso"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # 2014-02-17T10:38:43.910691Z
    tdata["_ltiso"] = datetime.now().isoformat()  # local time in iso format
    tdata["_dthhmm"] = dt.strftime("%H:%M")  # 10:16
    tdata["_dthhmmss"] = dt.strftime("%H:%M:%S")  # hhmmss=10:16:21

    return tdata


def xform(function: str, orig_value: t.Any, transform_data: TdataType) -> t.Union[TdataType, str, None]:
    """
    Attempt transformation on orig_value.

    - 1st. function()
    - 2nd. inline {xxxx}
    """

    if orig_value is None:
        return None

    res = orig_value

    if function is not None:
        try:
            function_name = sanitize_function_name(function)
            try:
                res = context.invoker.datamap(function_name, transform_data)
                return res
            except:
                logger.exception(f"Invoking function failed: {function}")
        except:
            pass

        try:
            res = Formatter().format(function, **transform_data)
        except:
            logger.exception(f"Formatting message with function failed: {function}")

    if isinstance(res, str):
        res = res.replace("\\n", "\n")

    return res


def decode_payload(section: str, topic: str, payload: t.Union[str, bytes]) -> TdataType:
    """
    Decode message payload through transformation machinery.
    """

    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except Exception as ex:
            logger.debug(f"Decoding from UTF-8 failed: {ex}. payload={truncate(payload)}")

    transform_data = builtin_transform_data(topic, payload)

    topic_data = context.get_topic_data(section, transform_data)
    if topic_data is not None and isinstance(topic_data, dict):
        transform_data.update(topic_data)

    # The dict returned is completely merged into transformation data
    # The difference between this and `get_topic_data()' is that this
    # function obtains the topic string as well as the payload and any
    # existing transformation data, and it can do 'things' with all.
    # This is the way it should originally have been, but I can no
    # longer fix the original (legacy).

    all_data = context.get_all_data(section, topic, transform_data)
    if all_data is not None and isinstance(all_data, dict):
        transform_data.update(all_data)

    # Gracefully attempt to decode the payload from JSON. If it's possible, add
    # the JSON keys into item to pass to the plugin, and create the outgoing
    # (i.e. transformed) message.
    try:
        if isinstance(payload, str):
            payload = payload.rstrip("\0")
        payload_data = json.loads(payload)
        transform_data.update(payload_data)
    except Exception as ex:
        logger.debug(f"Decoding JSON failed: {ex}. payload={truncate(payload)}")

    return transform_data


def processor(worker_id=None):
    """
    Queue runner. Pull a job from the queue, find the module in charge
    of handling the service, and invoke the module's plugin to do so.
    """
    while not exit_flag:
        logger.debug("Job queue has %s items to process" % q_in.qsize())
        job = q_in.get()
        if process_job(job=job, worker_id=worker_id):
            q_in.task_done()
    logger.debug("Worker thread exiting")


def process_job(job, worker_id=None):
    """
    Process a single job item.
    """

    if True:

        service = job.service
        section = job.section
        target = job.target
        topic = job.topic

        logger.debug("Processor #%s is handling: `%s' for %s" % (worker_id, service, target))

        # Sanity checks.
        # If service configuration or targets can not be obtained successfully,
        # log a sensible error message, fail the job, and carry on with the next job.
        try:
            service_config = context.get_service_config(service)
            service_targets = context.get_service_targets(service)

            if target not in service_targets:
                error_message = (
                    "Invalid configuration: Topic '{topic}' points to "
                    "non-existing target '{target}' in service '{service}'".format(**locals())
                )
                raise KeyError(error_message)

        except Exception:
            logger.exception(f"Cannot handle service={service}, target={target}")
            return True

        # Be more graceful with jobs w/o any target address information (2021-10-18 [amo]).
        if target is None:
            addrs = []
        else:
            addrs = service_targets[target]

        item = {
            "service": service,
            "section": section,
            "target": target,
            "config": service_config,
            "addrs": addrs,
            "topic": topic,
            "payload": job.payload,
            "data": None,
            "title": None,
            "image": None,
            "message": None,
            "priority": None,
        }

        transform_data = job.data
        item["data"] = dict(list(transform_data.items()))

        origin_title = "{}: {}".format(SCRIPTNAME, topic)
        item["title"] = xform(context.get_config(section, "title"), origin_title, transform_data)
        item["image"] = xform(context.get_config(section, "image"), "", transform_data)
        item["message"] = xform(context.get_config(section, "format"), job.payload, transform_data)

        try:
            item["priority"] = int(xform(context.get_config(section, "priority"), 0, transform_data))
        except:
            item["priority"] = 0
            logger.exception("Failed to determine the priority, defaulting to zero")

        if HAVE_JINJA is False and context.get_config(section, "template"):
            logger.warning("Templating not possible because Jinja2 is not installed")

        if HAVE_JINJA is True:
            template = context.get_config(section, "template")
            if template is not None:
                try:
                    text = render_template(template, transform_data)
                    if text is not None:
                        item["message"] = text
                except:
                    logger.exception(f"Rendering template failed: {template}")

        if item.get("message") is not None and len(item.get("message")) > 0:
            st = Struct(**item)
            notified = False
            logger.info("Invoking service plugin for `%s'" % service)
            try:
                # Fire the plugin in a separate thread and kill it if it doesn't return in 10s
                module = service_plugins[service]["module"]
                if "." in service:
                    service_logger_name = service
                else:
                    service_logger_name = "mqttwarn.services.{}".format(service)
                srv = make_service(mqttc=mqttc, name=service_logger_name)
                notified = timeout(module.plugin, (srv, st))
            except Exception as ex:
                logger.exception(f"Invoking service failed. Reason: {ex}. service={service}, topic={topic}")

            if not notified:
                logger.warning(f"Notification failed or timed out. service={service}, topic={topic}")
        else:
            logger.info(f"Notification suppressed. Reason: Payload is empty. service={service}, topic={topic}")

        return True


def load_services(services):

    if services is None:
        logger.warning("No services defined")
        return

    for service in services:
        service_plugins[service] = {}

        service_config = cf.config("config:" + service)
        service_plugins[service]["config"] = service_config

        module = cf.g("config:" + service, "module", service)

        # Load external service from file.
        modulefile_candidates = []
        if module.endswith(".py"):
            # Add two candidates: a) Use the file as given and b) treat the file as relative to
            # the directory of the configuration file. That retains backward compatibility.
            modulefile_candidates.append(module)
            modulefile_candidates.append(os.path.join(cf.configuration_path, module))

        # Load external service with module specification.
        elif "." in module:
            logger.debug('Trying to load service "{}" from module "{}"'.format(service, module))
            try:
                service_plugins[service]["module"] = load_module_by_name(module)
                logger.info('Successfully loaded service "{}" from module "{}"'.format(service, module))
                continue
            except:
                logger.exception('Loading service "{}" from module "{}" failed'.format(service, module))

        # Load built-in service module.
        else:
            # Backward-compatibility patch for honoring the renaming of the `http.py` module.
            if module == "http":
                module = "http_urllib"
            logger.debug('Trying to load built-in service "{}" from "{}"'.format(service, module))
            service_filename = module + ".py"
            service_filepath = resource_files("mqttwarn.services") / service_filename
            modulefile_candidates = [service_filepath]

        success = False
        for modulefile in modulefile_candidates:
            if not os.path.isfile(modulefile):
                logger.error('Module "{}" is not a file'.format(modulefile))
                continue
            logger.debug('Trying to load service "{}" from file "{}"'.format(service, modulefile))
            try:
                service_plugins[service]["module"] = load_module_from_file(modulefile)
                logger.info('Successfully loaded service "{}"'.format(service))
                success = True
            except:
                logger.exception(f'Loading service "{service}" from file "{modulefile}" failed')

        if not success:
            msg = "Failed loading service: {}".format(service)
            logger.critical(msg)
            raise ImportError(msg)


def connect():
    """
    Load service plugins, connect to the MQTT broker, launch daemon threads, and listen forever.
    """

    # FIXME: Remove global variables
    global mqttc

    try:
        services = cf.getlist("defaults", "launch")
    except:
        logger.error("No services configured, aborting")
        # TODO: Review this.
        sys.exit(2)

    load_services(services)

    # Initialize MQTT broker connection
    mqttc = paho.Client(cf.clientid, clean_session=cf.cleansession, protocol=cf.protocol)

    logger.debug("Attempting connection to MQTT broker %s:%d" % (cf.hostname, int(cf.port)))
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect

    # check for authentication
    if cf.username:
        mqttc.username_pw_set(cf.username, cf.password)

    # set the lwt before connecting
    if cf.lwt is not None:
        logger.debug("Setting LWT to %s" % (cf.lwt))
        mqttc.will_set(cf.lwt, payload=cf.lwt_dead, qos=0, retain=True)

    # Delays will be: 3, 6, 12, 24, 30, 30, etc.
    # mqttc.reconnect_delay_set(delay=3, delay_max=30, exponential_backoff=True)

    if cf.tls is True:
        mqttc.tls_set(cf.ca_certs, cf.certfile, cf.keyfile, tls_version=cf.tls_version, ciphers=None)

    if cf.tls_insecure:
        mqttc.tls_insecure_set(True)

    try:
        mqttc.connect(cf.hostname, int(cf.port), 60)

    except Exception:
        logger.exception("Cannot connect to MQTT broker at %s:%d" % (cf.hostname, int(cf.port)))
        # TODO: Review this.
        sys.exit(2)

    # Update our runtime context (used by functions etc) now we have a connected MQTT client
    context.invoker.srv.mqttc = mqttc

    # Publish status information to `mqttwarn/$SYS` topic.
    publish_status_information()

    # Launch worker threads to operate on queue
    start_workers()

    return mqttc


def subscribe_forever():
    mqttc = connect()
    while not exit_flag:
        reconnect_interval = 5

        try:
            mqttc.loop_forever()
        except socket.error as ex:
            logger.exception(f"Connection to MQTT broker lost: {ex.__class__.__name__}({ex})")
        except Exception as ex:
            logger.exception(f"Connection to MQTT broker lost: {ex.__class__.__name__}({ex})")
            raise

        if not exit_flag:
            logger.warning("MQTT server disconnected, trying to reconnect each %s seconds" % reconnect_interval)
            # TODO: Review this.
            time.sleep(reconnect_interval)


def publish_status_information():
    """
    Implement `$SYS` topic, like Mosquitto's "Broker Status".
    https://mosquitto.org/man/mosquitto-8.html#idm289

    Idea from Mosquitto::

      $ mosquitto_sub -t '$SYS/broker/version' -v
      $SYS/broker/version mosquitto version 2.0.10

    Synopsis::

      $ mosquitto_sub -t 'mqttwarn/$SYS/#' -v

      mqttwarn/$SYS/version 0.26.2
      mqttwarn/$SYS/platform darwin
      mqttwarn/$SYS/python/version 3.9.7

    """
    if cf.has_option("defaults", "status_publish") and cf.status_publish:

        status_topic = cf.g("defaults", "status_topic", "mqttwarn/$SYS")
        logger.info(f"Publishing status information to {status_topic}")

        # Items are tuples of (subtopic, message)
        si = StatusInformation()
        publications = [
            ("version", si.mqttwarn_version),
            ("platform", si.os_platform),
            ("python/version", si.python_version),
        ]
        try:
            for publication in publications:
                subtopic, message = publication
                mqttc.publish(status_topic + "/" + subtopic, message, retain=True)

        except:
            logger.exception("Unable to publish status information")


def start_workers():

    # Launch worker threads to operate on queue
    logger.info("Starting %s worker threads" % cf.num_workers)
    for i in range(cf.num_workers):
        t = threading.Thread(target=processor, kwargs={"worker_id": i})
        t.daemon = True
        t.start()

    # If the config file has a [cron] section, the key names therein are
    # functions from 'myfuncs.py' which should be invoked periodically.
    # The key's value (must be numeric!) is the period in seconds.

    if cf.has_section("cron"):
        for name, val in cf.items("cron"):
            try:
                func = load_function(name=name, py_mod=cf.functions)
            except AttributeError:
                logger.error("[cron] section has function [%s] specified, but that's not defined" % name)
                continue

            cron_options = parse_cron_options(val)
            interval = cron_options["interval"]
            logger.info(
                "Scheduling periodic task '{name}' to run each "
                "{interval} seconds via [cron] section".format(name=name, interval=interval)
            )
            service = make_service(mqttc=mqttc, name="mqttwarn.cron")
            ptlist[name] = PeriodicThread(
                callback=func, period=interval, name=name, srv=service, now=asbool(cron_options.get("now"))
            )
            ptlist[name].start()


def cleanup(signum=None, frame=None):
    """
    Signal handler to ensure we disconnect cleanly
    in the event of a SIGTERM or SIGINT.
    """
    for ptname in ptlist:
        logger.info(f"Cancelling periodic task '{ptname}'")
        ptlist[ptname].cancel()

    logger.debug("Disconnecting from MQTT broker")
    if cf.lwt is not None:
        mqttc.publish(cf.lwt, cf.lwt_dead, qos=0, retain=True)
    mqttc.loop_stop()
    mqttc.disconnect()

    logger.info("Waiting for queue to drain")
    q_in.join()

    # Send exit signal to subsystems _after_ queue was drained.
    # TODO: Refactor this elsewhere.
    global exit_flag
    exit_flag = True

    # TODO: Refactor this elsewhere.
    logger.debug(f"Exiting on signal {signum}")
    # TODO: Review this.
    sys.exit(signum)


def bootstrap(config=None, scriptname=None):
    # FIXME: Remove global variables
    global context, cf, SCRIPTNAME
    # NOTE: this is called before we connect to the MQTT broker, so mqttc is not initialised yet
    invoker = FunctionInvoker(config=config, srv=make_service(mqttc=None, name="mqttwarn.context"))
    context = RuntimeContext(config=config, invoker=invoker)
    cf = config
    if scriptname is not None:
        SCRIPTNAME = scriptname


def run_plugin(config=None, name=None, options=None, data=None, message=None):
    """
    Run service plugins directly without the
    dispatching and transformation machinery.

    On the one hand, this might look like a bit of a hack.
    On the other hand, it shows very clearly how some of
    the innards of mqttwarn interact so it might also please
    newcomers as a "learning the guts of mqttwarn" example.

    :param config:   The configuration object
    :param name:     The name of the service plugin, e.g. "log" or "file"
    :param options:  The data to be converged into an appropriate item Struct object instance
    """

    # Bootstrap mqttwarn core
    # TODO: Optionally run w/o configuration.
    bootstrap(config=config)

    # Load designated service plugins
    load_services([name])
    if "." in name:
        service_logger_name = name
    else:
        service_logger_name = "mqttwarn.services.{}".format(name)
    srv = make_service(mqttc=None, name=service_logger_name)

    # Build a mimikry item instance for feeding to the service plugin
    item = Struct(**options or {})
    # TODO: Read configuration optionally from data.
    item.config = config.config("config:" + name)
    item.service = srv
    item.target = "mqttwarn"
    item.data = data or {}
    if not hasattr(item, "message"):
        item.message = message

    # Launch plugin
    module = service_plugins[name]["module"]
    response = module.plugin(srv, item)
    logger.info("Plugin response: {}".format(response))
    if response is False:
        sys.exit(1)
