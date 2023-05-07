# -*- coding: utf-8 -*-
# (c) 2014-2023 The mqttwarn developers
import logging
import typing as t

import attr

from mqttwarn.configuration import Config
from mqttwarn.model import Service, TdataType, TopicTargetType
from mqttwarn.util import load_function, sanitize_function_name

logger = logging.getLogger(__name__)


@attr.s
class RuntimeContext:
    """
    This carries runtime information and provides the core
    with essential methods for accessing the configuration
    and for invoking parts of the transformation machinery.
    """

    config: Config = attr.ib()
    invoker: "FunctionInvoker" = attr.ib()

    def get_sections(self) -> t.List[str]:
        sections = []
        for section in self.config.sections():
            if section == "defaults":
                continue
            if section == "cron":
                continue
            if section == "failover":
                continue
            if section.startswith("config:"):
                continue
            if self.config.has_option(section, "targets"):
                sections.append(section)
            else:
                logger.warning("Section `%s' has no targets defined" % section)
        return sections

    def get_topic(self, section: str) -> str:
        if self.config.has_option(section, "topic"):
            return self.config.get(section, "topic")
        return section

    def get_qos(self, section: str) -> int:
        qos = 0
        if self.config.has_option(section, "qos"):
            qos = int(self.config.get(section, "qos"))
        return qos

    def get_config(self, section: str, name: str) -> t.Any:
        value = None
        if self.config.has_option(section, name):
            value = self.config.get(section, name)
        return value

    def is_filtered(self, section: str, topic: str, payload: t.AnyStr) -> bool:
        if self.config.has_option(section, "filter"):
            try:
                name = sanitize_function_name(self.config.get(section, "filter"))
                return self.invoker.filter(name, topic, payload, section)
            except Exception as e:
                logger.exception("Cannot invoke filter function '%s' defined in '%s': %s" % (name, section, e))
        return False

    def get_topic_data(self, section: str, data: TdataType) -> t.Optional[TdataType]:
        if self.config.has_option(section, "datamap"):
            try:
                name = sanitize_function_name(self.config.get(section, "datamap"))
                return self.invoker.datamap(name, data)
            except Exception as e:
                logger.exception("Cannot invoke datamap function '%s' defined in '%s': %s" % (name, section, e))
        return None

    def get_all_data(self, section: str, topic: str, data: TdataType) -> t.Optional[TdataType]:
        if self.config.has_option(section, "alldata"):
            try:
                name = sanitize_function_name(self.config.get(section, "alldata"))
                return self.invoker.alldata(name, topic, data)
            except Exception as e:
                logger.exception("Cannot invoke alldata function '%s' defined in '%s': %s" % (name, section, e))
        return None

    def get_topic_targets(self, section: str, topic: str, data: TdataType) -> TopicTargetType:
        """
        Topic targets function invoker.
        """
        if self.config.has_option(section, "targets"):
            try:
                name = sanitize_function_name(self.config.get(section, "targets"))
                return self.invoker.topic_target_list(name, topic, data)
            except Exception as ex:
                error = repr(ex)
                logger.warning(
                    'Error invoking topic targets function "{name}" '
                    'defined in section "{section}": {error}'.format(**locals())
                )
        return None

    def get_service_config(self, service: str) -> t.Dict[str, t.Any]:
        config = self.config.config("config:" + service)
        if config is None:
            return {}
        return dict(config)

    def get_service_targets(self, service: str) -> t.List[TopicTargetType]:
        """
        Resolve target address descriptor.

        2021-10-18 [amo]: Be more graceful with jobs w/o any target address information.
        """
        targets: t.List[TopicTargetType] = self.config.getdict("config:" + service, "targets")

        # TODO: The target address descriptor may be of any type these days,
        #       and not necessarily a list.
        # TODO: Currently, make sure to always return one element.
        #       Verify if this is really needed.
        targets = targets or [None]
        return targets


@attr.s
class FunctionInvoker:
    """
    This helps the ``RuntimeContext`` to dynamically invoke
    functions from a configured Python source code file.
    """

    config: Config = attr.ib()
    srv: Service = attr.ib()

    def datamap(self, name: str, data: TdataType) -> TdataType:
        """
        Invoke function "name" loaded from the "functions" Python module.

        :param name:    Function name to invoke
        :param data:    Data to pass to the invoked function
        :return:        Return value of function invocation
        """

        val = None

        try:
            func = load_function(name=name, py_mod=self.config.functions)
            try:
                val = func(data, self.srv)  # new version
            except TypeError:
                val = func(data)  # legacy
        except:
            raise

        return val

    def alldata(self, name: str, topic: str, data: TdataType) -> TdataType:
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

    def topic_target_list(self, name: str, topic: str, data: TdataType) -> TopicTargetType:
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

    def filter(self, name: str, topic: str, payload: t.AnyStr, section: t.Optional[str] = None) -> bool:  # noqa:A003
        """
        Invoke function "name" loaded from the "functions" Python module.
        Return that function's True/False.

        :param name:    Function name to invoke
        :param topic:   Topic to pass to the invoked function
        :param payload: Payload to pass to the invoked function
        :return:        Return value of function invocation
        """

        # Filtering currently only works on text.
        # TODO: To let filtering also work on binary data, this line would need to go elsewhere. But where?
        if isinstance(payload, bytes):
            payload_decoded = payload.decode("utf-8")
        else:
            payload_decoded = payload

        rc = False
        try:
            func = load_function(name=name, py_mod=self.config.functions)
            try:
                rc = func(topic, payload_decoded, section, self.srv)  # new version
            except TypeError:
                rc = func(topic, payload_decoded)  # legacy signature
        except:
            raise

        return rc
