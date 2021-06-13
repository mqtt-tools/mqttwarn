# -*- coding: utf-8 -*-
# (c) 2014-2019 The mqttwarn developers
from builtins import object
import attr
import logging

from mqttwarn.util import sanitize_function_name, load_function

logger = logging.getLogger(__name__)


@attr.s
class RuntimeContext(object):
    """
    This carries runtime information and provides the core
    with essential methods for accessing the configuration
    and for invoking parts of the transformation machinery.
    """

    config = attr.ib()
    invoker = attr.ib()

    def get_sections(self):
        sections = []
        for section in self.config.sections():
            if section == 'defaults':
                continue
            if section == 'cron':
                continue
            if section == 'failover':
                continue
            if section.startswith('config:'):
                continue
            if self.config.has_option(section, 'targets'):
                sections.append(section)
            else:
                logger.warn("Section `%s' has no targets defined" % section)
        return sections

    def get_topic(self, section):
        if self.config.has_option(section, 'topic'):
            return self.config.get(section, 'topic')
        return section

    def get_qos(self, section):
        qos = 0
        if self.config.has_option(section, 'qos'):
            qos = int(self.config.get(section, 'qos'))
        return qos

    def get_config(self, section, name):
        value = None
        if self.config.has_option(section, name):
            value = self.config.get(section, name)
        return value

    def is_filtered(self, section, topic, payload):
        if self.config.has_option(section, 'filter'):
            filterfunc = sanitize_function_name( self.config.get(section, 'filter') )
            try:
                return self.invoker.filter(filterfunc, topic, payload, section)
            except Exception as e:
                logger.warn("Cannot invoke filter function %s defined in %s: %s" % (filterfunc, section, e))
        return False

    def get_topic_data(self, section, topic):
        if self.config.has_option(section, 'datamap'):
            name = sanitize_function_name(self.config.get(section, 'datamap'))
            try:
                return self.invoker.datamap(name, topic)
            except Exception as e:
                logger.warn("Cannot invoke datamap function %s defined in %s: %s" % (name, section, e))
        return None

    def get_all_data(self, section, topic, data):
        if self.config.has_option(section, 'alldata'):
            name = sanitize_function_name(self.config.get(section, 'alldata'))
            try:
                return self.invoker.alldata(name, topic, data)
            except Exception as e:
                logger.warn("Cannot invoke alldata function %s defined in %s: %s" % (name, section, e))
        return None

    def get_topic_targets(self, section, topic, data):
        """
        Topic targets function invoker.
        """
        if self.config.has_option(section, 'targets'):
            name = sanitize_function_name(self.config.get(section, 'targets'))
            try:
                return self.invoker.topic_target_list(name, topic, data)
            except Exception as ex:
                error = repr(ex)
                logger.warn('Error invoking topic targets function "{name}" ' \
                             'defined in section "{section}": {error}'.format(**locals()))
        return None

    def get_service_config(self, service):
        config = self.config.config('config:' + service)
        if config is None:
            return {}
        return dict(config)

    def get_service_targets(self, service):
        try:
            targets = self.config.getdict('config:' + service, 'targets')
            if type(targets) != dict:
                logger.error("No targets for service `%s'" % service)
        except:
            logger.error("No targets for service `%s'" % service)

        if targets is None:
            return {}

        return dict(targets)


@attr.s
class FunctionInvoker(object):
    """
    This helps the ``RuntimeContext`` to dynamically invoke
    functions from a configured Python source code file.
    """

    config = attr.ib()
    srv = attr.ib()

    def datamap(self, name, topic):
        """
        Invoke function "name" loaded from the "functions" Python module.

        :param name:    Function name to invoke
        :param topic:   Topic to pass to the invoked function
        :return:        Return value of function invocation
        """

        val = None
        try:
            func = load_function(name=name, py_mod=self.config.functions)
            try:
                val = func(topic, self.srv)  # new version
            except TypeError:
                val = func(topic)       # legacy
        except:
            raise

        return val

    def alldata(self, name, topic, data):
        """
        Invoke function "name" loaded from the "functions" Python module.

        :param name:    Function name to invoke
        :param topic:   Topic to pass to the invoked function
        :param data:    Data to pass to the invoked function
        :return:        Return value of function invocation
        """

        val = None
        try:
            func = load_function(name=name, py_mod=self.config.functions)
            val = func(topic, data, self.srv)
        except:
            raise

        return val

    def topic_target_list(self, name, topic, data):
        """
        Invoke function "name" loaded from the "functions" Python module.
        Computes dynamic topic subscription targets.
        Obtains MQTT topic and transformation data.

        :param name:    Function name to invoke
        :param topic:   Topic to pass to the invoked function
        :param data:    Data to pass to the invoked function
        :return:        Return value of function invocation
        """

        val = None
        try:
            func = load_function(name=name, py_mod=self.config.functions)
            val = func(topic=topic, data=data, srv=self.srv)
        except:
            raise

        return val

    def filter(self, name, topic, payload, section=None):
        """
        Invoke function "name" loaded from the "functions" Python module.
        Return that function's True/False.

        :param name:    Function name to invoke
        :param topic:   Topic to pass to the invoked function
        :param payload: Payload to pass to the invoked function
        :return:        Return value of function invocation
        """

        rc = False
        try:
            func = load_function(name=name, py_mod=self.config.functions)
            try:
                rc = func(topic, payload, section, self.srv)  # new version
            except TypeError:
                rc = func(topic, payload)                     # legacy signature
        except:
            raise

        return rc
