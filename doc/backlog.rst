#############
mqttwarn todo
#############

Task: Make mqttwarn a first citizen of the Python ecosystem.


****************
Goals for 0.20.0
****************
- [o] Improve software tests
- [o] Refactor contents from "examples", "templates" and "vendor" folders
      - The path to the "templates" folder must be specified using command line argument or environment variable.
            Otherwise, look nearby the configuration file /path/to/mqttwarn.ini, so use /path/to/templates.
      - Integrate existing template .j2 files into example folder?
- [o] Add some entrypoints
      - Wire ``contrib/amqp-puka-get.py`` to ``mqttwarn --plugin=amqp --command=subscribe``
      - Wire ``contrib/zabbix_mqtt_agent.py`` to ``mqttwarn --plugin=zabbix --command=publish``
      - Wire ``mqttwarn/vendor/ZabbixSender.py`` to ``mqttwarn --plugin=zabbix --command=sensor``
- [o] How to address "samplefuncs.py" in relation to "mqttwarn.ini"? E.g. if the mqttwarn configuration file
      would be ``/etc/mqttwarn/acme.ini``, should this load ``/etc/mqttwarn/samplefuncs.py`` or use the current
      working directory for that? Or even both!?
- [o] When running the mqttwarn daemon and no configuration file is given,
      use configuration from the ".mqttwarn" folder in the current working directory.
      When doing so, also use ".mqttwarn/templates" as the default templates folder.
- [o] Verify that "functions" still accepts file names as well as dotted module names
- [o] Adapt configuration for Supervisor and systemd
- [o] Improve documentation: Add a complete roundtrip example involving ``mosquitto_pub``
- [o] Improve documentation: Add "credits" section. At least add the author of Mosquitto.
- [o] Add ``mqttwarn make-pubs`` or ``mqttwarn selftest``, see https://github.com/jpmens/mqttwarn/issues/127#issuecomment-381690557
- [o] Improve logging: Let "file" service report about where it's writing to


****************
Goals for 0.21.0
****************
- [o] Refactor the ``mqttwarn make-config|make-samplefuncs`` machinery into a ``mqttwarn init``-style thing. Proposal::

      # Create folder .mqttwarn with minimal configuration (config.ini, custom.py)
      mqttwarn init

      # Create folder .mqttwarn with configuration from named preset "hiveeyes" (hiveeyes.ini, hiveeyes.py, hiveeyes-alert.j2)
      mqttwarn init --preset=hiveeyes

      # Create folder .mqttwarn with configuration from named preset "homie" (homie.ini, homie.py)
      mqttwarn init --preset=homie


***************
Goals for 1.0.0
***************
- [o] Make mqttwarn completely unicode-safe
- [o] Make "mqttwarn --plugin=log --options=" obtain JSON data from STDIN
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
      to [Munin](http://munin-monitoring.org/)'s
      [autoconf](http://guide.munin-monitoring.org/en/latest/develop/plugins/plugin-concise.html#autoconf) and
      [suggest](http://guide.munin-monitoring.org/en/latest/develop/plugins/plugin-concise.html#suggest) features.
      So, let's pretend invoking::

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
      https://github.com/jpmens/mqttwarn/issues/283
- [o] Configuration and source tree file watcher like ``pserve ... --reload``
