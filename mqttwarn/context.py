# -*- coding: utf-8 -*-
# (c) 2014-2018 The mqttwarn developers
import attr
import logging

from mqttwarn.util import sanitize_function_name, load_function

logger = logging.getLogger(__name__)


@attr.s
class RuntimeContext(object):

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
                return self.invoker.filter(filterfunc, topic, payload)
            except Exception, e:
                logger.warn("Cannot invoke filter function %s defined in %s: %s" % (filterfunc, section, str(e)))
        return False

    def get_topic_data(self, section, topic):
        if self.config.has_option(section, 'datamap'):
            name = sanitize_function_name(self.config.get(section, 'datamap'))
            try:
                return self.invoker.datamap(name, topic)
            except Exception, e:
                logger.warn("Cannot invoke datamap function %s defined in %s: %s" % (name, section, str(e)))
        return None

    def get_all_data(self, section, topic, data):
        if self.config.has_option(section, 'alldata'):
            name = sanitize_function_name(self.config.get(section, 'alldata'))
            try:
                return self.invoker.alldata(name, topic, data)
            except Exception, e:
                logger.warn("Cannot invoke alldata function %s defined in %s: %s" % (name, section, str(e)))
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



@attr.s
class FunctionInvoker(object):

    config = attr.ib()
    srv = attr.ib()

    def datamap(self, name, topic):
        ''' Attempt to invoke function `name' loaded from the
            `functions' Python package '''

        val = None

        try:
            func = load_function(name=name, filepath=self.config.functions)
            try:
                val = func(topic, self.srv)  # new version
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
            func = load_function(name=name, filepath=self.config.functions)
            val = func(topic, data, self.srv)
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
            func = load_function(name=name, filepath=self.config.functions)
            val = func(topic=topic, data=data, srv=self.srv)
        except:
            raise

        return val

    def filter(self, name, topic, payload):
        ''' Attempt to invoke function `name' from the `functions'
            package. Return that function's True/False '''

        rc = False
        try:
            func = load_function(name=name, filepath=self.config.functions)
            rc = func(topic, payload)
        except:
            raise

        return rc
