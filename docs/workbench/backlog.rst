################
mqttwarn backlog
################


************
Iteration +1
************

Next
====
- [o] Frigate: Rename goat.png to goat.jpg
- [o] Test ``test_system_dispatch_to_log_service_plaintext`` is flaky on CI
- [o] Test ``test_subscribe_forever_fails_socket_error`` is flaky on CI

  - https://github.com/jpmens/mqttwarn/actions/runs/4839474570/jobs/8624518352?pr=649#step:7:421
- [o] https://mqttwarn.readthedocs.io/en/latest/usage/index.html#configuration-file is not enough,
  because it already references an ``udf.py`` file, which needs to be created using ``mqttwarn
  make-udf``.

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
- [o] Add documentation snippet to ntfy

  - https://github.com/binwiederhier/ntfy/blob/main/docs/integrations.md
  - À la https://docs.ntfy.sh/examples/#traccar, but for OwnTracks
- [o] Tutorial: MQTT topic rewriting with mqttwarn
- [o] Tutorial: Periodic MOTD notifier with ntfy
- [o] Document ``mqttwarn.util``, like ``load_file()``
- [o] Refactor "README » Running as system daemon" into documentation.
- [o] Re-add::

    There are also some extensions to mqttwarn not included in the core package.
    Instead, they are bundled into another package, ``mqttwarn-contrib``, see also
    `community contributions to mqttwarn`_.
- [o] Python <-> Go bindings
  - https://github.com/tliron/py4go
  - https://github.com/sbinet/go-python
  - https://github.com/qur/gopy
  - https://github.com/go-python/gopy
  - https://github.com/asottile/setuptools-golang
  - https://github.com/dop251/goja
  - https://github.com/robertkrimen/otto
  - https://github.com/traefik/yaegi
  - https://github.com/tetratelabs/wazero
  - https://github.com/wasmerio/wasmer-go
  - https://github.com/dbohdan/embedded-scripting-languages

- [o] Example for ``mqttwarn-contrib``: https://github.com/jpmens/mqttwarn/issues/526#issuecomment-864423040
- [o] Tutorial with Wetterdienst
- [o] MQTT republishing and topic rewriting

  - https://hiveeyes.org/docs/beradio/research/mqtt.html
  - https://lodge.glasgownet.com/2012/09/23/mqtt-republishing-itch/
  - https://github.com/kylegordon/mqtt-republisher
  - https://docs.aws.amazon.com/iot/latest/developerguide/iot-repub-rule.html
  - https://docs.netscaler.com/en-us/citrix-adc/current-release/appexpert/rewrite/mqtt-support-rewrite.html
  - https://groups.google.com/g/mqtt/c/lUrwt9p2NDk
  - https://emqx.medium.com/emq-x-mqtt-5-0-topic-rewrite-b3728427cf8c

- [o] https://github.com/padelt/docker-owntracks-private-mqtt-broker
- [o] https://cedalo.com/blog/best-mqtt-tools/


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
- [o] Only ship a single OCI image?
  https://github.com/jpmens/mqttwarn/pull/645#discussion_r1180798080
- [o] https://github.com/eclipse/paho.mqtt.testing
- [o] Support MQTT Sparkplug?

  - https://modelbasedtesting.co.uk/2022/01/22/getting-started-with-mqtt-and-sparkplug/
  - https://cirrus-link.com/mqtt-sparkplug-tahu/
  - https://www.youtube.com/watch?v=-9vMAe7P25A
  - https://github.com/eclipse/tahu/blob/master/python/examples/example.py
  - https://github.com/eclipse/tahu/blob/master/python/examples/example_simple.py
  - https://newsroom.eclipse.org/eclipse-newsletter/2023/february/sparkplug-30-brings-cleaner-implementations-and-greater
- [o] Use ``outgoing`` for email plugin?
  https://github.com/jwodder/outgoing


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
