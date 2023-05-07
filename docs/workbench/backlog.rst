################
mqttwarn backlog
################


************
Iteration +1
************

Bugs
====
- [o] Documentation vs. code: Clarify and/or fix logic of "filter" function
  https://github.com/mqtt-tools/mqttwarn/issues/637

Features
========
- [o] Start even when MQTT broker is not available

Maintenance
===========
- [o] mqttwarn/util.py:5: DeprecationWarning: the imp module is deprecated in favour of importlib
- [o] pytest-mqtt: Truncate message output
- [o] Remove deprecated ``mqttwarn.services.apprise``

Documentation » Tech
====================
- [x] Add documentation on RTD
  https://github.com/mqtt-tools/mqttwarn/issues/389#issuecomment-1428353079
- [x] ogp-metadata-plugin
- [x] sphinx-copybutton
- [x] sphinx-autodoc
- [x] Collapsibles
- [o] Mermaid?
- [o] Grid on bottom of landing page
- [o] automodules
- [o] Refactor backlog.rst to use MyST tasklists
- [o] Does ``html_show_sourcelink`` actually work?
  https://github.com/pradyunsg/furo/issues/12
- [o] Enable ``html_use_opensearch``?
  https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_use_opensearch

Documentation » Content
=======================
- [x] Refactor "Services"
- [x] Refactor "Topics"
- [x] New: Configuration at a glance / in a nutshell / Introduction
- [x] Move "Press" into more prominent section
- [x] Refactor "Plugins"
- [x] Refactor "Examples" / "Tutorials"
- [x] Code example for "Transformation » Decoding nested JSON" section
- [x] Naming things: Replace term "custom function" with "user-defined function" (UDF)

- [o] Search for all old links
- [o] Better advertise the new configuration section layout for ``targets``,
  it can be strings (ntfy), or dictionaries (ntfy, pushsafer)
- [o] Improve default output for ``mqttwarn make-udf``, ``basic/udf.py``.
- [o] Deprecate the ``datamap`` function. ``alldata`` is the new thing.
- [o] Screen the Wiki for more content
  https://github.com/mqtt-tools/mqttwarn/wiki/Incorporating-topic-names#incorporate-topic-names-into-topic-targets
- [o] Naming things: "Transforming" is actually "Decoding"
- [o] Add example from https://jpmens.net/2018/03/25/alerting-on-ssh-logins/
- [o] Add "Acknowledgements" section
- [o] Add decoder function to "Templated targets" example
  https://mqttwarn.readthedocs.io/en/latest/configure/topic.html#example-2
- [o] What about the `item` definition in ...? Is it actually the real "transformation data" now?
  https://mqttwarn.readthedocs.io/en/latest/configure/service.html#creating-custom-notification-plugins

- [o] The ``format`` option should be renamed to ``message`` or ``body``
- [o] Rename ``alldata`` to ``decode``, or ``decoder``
- [o] Add documentation snippet to ntfy, à la https://docs.ntfy.sh/examples/#traccar, but for OwnTracks
- [o] Tutorial: MQTT topic rewriting with mqttwarn
- [o] Tutorial: Periodic MOTD notifier with ntfy
- [o] Document ``mqttwarn.util``, like ``load_file()``
- [o] Refactor "README » Running as system daemon" into documentation.
- [o] Re-add::

    There are also some extensions to mqttwarn not included in the core package.
    Instead, they are bundled into another package, ``mqttwarn-contrib``, see also
    `community contributions to mqttwarn`_.

.. _community contributions to mqttwarn: https://pypi.org/project/mqttwarn-contrib/


************
Iteration +2
************
- [o] Enable doctests with pytest
- [o] ntfy: Allow to set tags per mqttwarn.ini
- [o] ntfy: Allow to configure to use ntfy.sh by only providing the topic
- [o] Improve topic decoding: What about writing decoder functions in JavaScript?
- [o] Improve software tests
- [o] Refactor contents from "examples", "templates" and "vendor" folders

  - The path to the "templates" folder must be specified using command line argument or environment variable.
    Otherwise, look nearby the configuration file /path/to/mqttwarn.ini, so use /path/to/templates.
  - Integrate existing template .j2 files into example folder?
- [o] Think about introducing mqttwarn "applications", made of user-defined function files,
  and corresponding configurations.
- [o] Add some entrypoints

  - Wire ``contrib/amqp-puka-get.py`` to ``mqttwarn --plugin=amqp --command=subscribe``
  - Wire ``contrib/zabbix_mqtt_agent.py`` to ``mqttwarn --plugin=zabbix --command=publish``
  - Wire ``mqttwarn/vendor/ZabbixSender.py`` to ``mqttwarn --plugin=zabbix --command=sensor``
- [o] How to address ``udf.py`` in relation to "mqttwarn.ini"? E.g. if the mqttwarn configuration file
  would be ``/etc/mqttwarn/acme.ini``, should this load ``/etc/mqttwarn/udf.py`` or use the current
  working directory for that? Or even both!?
- [o] When running the mqttwarn daemon and no configuration file is given,
  use configuration from the ".mqttwarn" folder in the current working directory.
  When doing so, also use ".mqttwarn/templates" as the default templates folder.
- [o] Verify that "functions" still accepts file names as well as dotted module names
- [o] Adapt configuration for Supervisor and systemd
- [o] Improve documentation: Add a complete roundtrip example involving ``mosquitto_pub``
- [o] Improve documentation: Add "credits" section. At least add the author of Mosquitto.
- [o] Add ``mqttwarn make-pubs`` or ``mqttwarn selftest``, see https://github.com/mqtt-tools/mqttwarn/issues/127#issuecomment-381690557
- [o] Improve logging: Let "file" service report about where it's writing to


************
Iteration +3
************
- [o] Refactor the ``mqttwarn make-config|make-udf`` machinery into a ``mqttwarn init``-style thing. Proposal::

      # Create folder .mqttwarn with minimal configuration (config.ini, udf.py)
      mqttwarn init

      # Create folder .mqttwarn with configuration from named preset "hiveeyes" (hiveeyes.ini, hiveeyes.py, hiveeyes-alert.j2)
      mqttwarn init --preset=hiveeyes

      # Create folder .mqttwarn with configuration from named preset "homie" (homie.ini, homie.py)
      mqttwarn init --preset=homie


***************
Goals for 1.0.0
***************
- [o] Make mqttwarn completely unicode-safe
- [o] Make ``mqttwarn --plugin=log --options=`` obtain JSON data from STDIN
- [o] Translate documentation into reStructuredText format,
  render it using Sphinx and optionally publish to readthedocs.org.
- [o] Add support for Python 3
- [o] Add activity indicator for running a) interactively (snappy) or b) daemonized (in interval).
  Display "tps" and general activity on a per-message basis.


***************
Goals for 2.0.0
***************
- [o] Idea: What if we could reuse the notification plugins in the context of a ``heronotify`` entrypoint?
- [o] Idea: It would be cool if mqttwarn could offer some kind of plugin autoconfiguration mechanism similar
  to `Munin`_'s `autoconf`_ and `suggest`_ features. So, let's pretend invoking::

        mqttwarn --plugin=telegram --suggest-config

      would offer this snippet on STDOUT for convenient configuration on your fingertips::

        [config:telegram]
        timeout = 60
        parse_mode = 'Markdown'
        token = 'mmmmmmmmm:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        use_chat_id = False
        targets = {
           #        First Name or @username or #chat_id
           'j01' : [ 'First Name' ],
           'j02' : [ '@username' ],
           'j03' : [ '#chat_id' ]
        }

      My proposal would be to add this mqttwarn in the most possible KISS-style. There should/might be an additional
      per-plugin function called ``suggest_config()`` à la::

        def suggest_config():
            snippet = """
            ...
            """
            return snippet
- [o] Think about adding further support for plugins, e.g. for provisioning databases appropriately, see also
  https://github.com/mqtt-tools/mqttwarn/issues/283
- [o] Configuration and source tree file watcher like ``pserve ... --reload``


.. _autoconf: https://guide.munin-monitoring.org/en/latest/develop/plugins/plugin-concise.html#autoconf
.. _Munin: https://munin-monitoring.org/
.. _suggest: https://guide.munin-monitoring.org/en/latest/develop/plugins/plugin-concise.html#suggest
