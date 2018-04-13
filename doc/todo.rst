#############
mqttwarn todo
#############

Task: Make mqttwarn a first citizen of the Python ecosystem.


****************
Goals for 0.15.0
****************
- [x] Refactoring. Move "services" into module namespace.
- [x] Put example "mqttwarn.ini" into resources folder of module namespace,
      add "mqttwarn make-config" and "mqttwarn make-samplefuncs"  commands to dump them to stdout
- [x] Add Makefile for releasing and documentation building
- [o] Refactor contents from "examples", "templates" and "vendor" folders
    - [o] Integrate templates into basic example?
    - [o] Move the whole /examples folder into /mqttwarn/examples?
    - [o] Where to put /templates and /vendor?
- [o] How to address "samplefuncs.py" in relation to "mqttwarn.ini"? E.g. if the mqttwarn configuration file
      would be ``/etc/mqttwarn/acme.ini``, should this load ``/etc/mqttwarn/samplefuncs.py`` or use the current
      working directory for that? Or even both!?
- [o] Adapt configuration for Supervisor and systemd
- [o] Check the zabbix and other modules
- [o] Release on PyPI


***************
Goals for 1.0.0
***************
- [o] Translate documentation into reStructuredText format,
      render it using Sphinx and optionally publish to readthedocs.org.
- [o] Add software tests
- [o] Add support for Python 3


***************
Goals for 2.0.0
***************
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


*************
This and that
*************
- [o] Add more eye candy to README.rst

    - Logo:
        - https://cloud.githubusercontent.com/assets/2345521/6320105/4dd7a826-bade-11e4-9a61-72aa163a40a9.png
        - https://github.com/jpmens/mqttwarn/issues/81#issuecomment-75520401

- [o] Improve logging: Let "file" service report about where it's writing to
