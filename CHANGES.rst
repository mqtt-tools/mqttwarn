##################
mqttwarn changelog
##################


in progress
===========


2021-06-19 0.26.1
=================

- Attempt to fix README on Docker Hub


2021-06-19 0.26.0
=================

- When title is not set in configuration settings, use ``mqttwarn: {topic}``
  instead of ``mqttwarn`` only. Thanks, Rob!
- Add launch configuration for VSCode. Thanks, David!
- Use STDERR as default log target
- Stop including the "tests" folder into the sdist package
- Add "mqttwarn-contrib" package to the list of "extra" dependencies
- Improve launching service plugins interactively from the command line
  Now, there are two options "--config" and "--options" to be able to
  obtain all relevant bits of information from the command line.


2021-06-18 0.25.0
=================

- Rename repository default branch to "main"
- Fix "http" service plugin
- Improve machinery to launch a notification service plugin standalone.
  Now, it works without any ``mqttwarn.ini`` configuration file at all.
- Begin adding tests for services
- Drop official support for Python 2


2021-06-12 0.24.0
=================

- [prowl] Update service plugin to use "pyprowl" instead of "prowlpy"
- [core] Make "functions" setting in configuration file optional
- [ci] Build and publish Docker multi-platform images


2021-06-08 0.23.1
=================

- [ci] Run software tests and Docker image building on GitHub Actions (GHA)
- [ci] Publish Docker images to GitHub Container Registry (GHCR)


2021-06-03 0.23.0
=================

- [http] Rename ``http.py`` module to ``http_urllib.py`` to reduce conflicts with stdlib.
  For backward compatibility reasons, it is still available by the same name, so no
  configurations will break. Thanks, Morten!


2021-06-03 0.22.0
=================

- [build] Fix unwanted cache hits when automatically building Docker images. Thanks, Gergő!
- [core] Respect relative path names within configuration file. This applies
  to both the function file as well as module files.


2021-06-03 0.21.0
=================
- [xmpp] Add slixmpp plugin and documentation. Thanks, Remi!
- [mysql] Fix unicode vs byte issue for Python 3. Thanks, Filip!
- [http] Fix to send whole message. Thanks, Gergő!
- [slack] Replace ``slacker`` with ``slack-sdk``. Thanks, mcdamo!
- [mysql] Fix specified port bug. Thanks, Hyman!
- [launch] Add new service ``launch``. Flexible arguments for command,
  responds with MQTT publish. Thanks, Jörg!
- [core] Remove "os.chdir" as it is apparently not needed anymore. Thanks, Dan!
- [ci] Run tests on Python 3.9, remove testing on Python 3.5
- [core] Load service plugins from both modules and files.


2020-10-20 0.20.0
=================
- [telegram] Fix encoding of data for python3. Thanks, Ben!


2020-10-11 0.19.0
=================
- [xbmc] Fix encoding of data for python3. Thanks, Ben!
- [hipchat, ionic, pushsafer] Fix charset encoding. Thanks, JP!
- [telegram] Add compatibility for both Python 2 and Python 3. Thanks, @clach04!
- Add new service for Chromecast TTS. Thanks, @clach04!
- Add example for Amazon Alexa Say/Announce. Thanks, @clach04!
- Improve documentation. Thanks, @clach04!
- Fix Apprise service by explicitly using legacy/synchronous mode.
- Add Python 3.9 support


2020-08-31 0.18.0
=================
- Use ``allow_dirty = False`` within ``.bumpversion.cfg``
- Use Python3 to create virtualenv
- Bump version numbers for release tools packages
- Add external plugin module loading. Thanks, @psyciknz!
- Replaced iothub service with azure-iot, just using MQTT. Thanks, Morten!


2020-08-31 0.17.0
=================
- srv.mqttc is None when calling into a custom function. Thanks, Ben.
- sundry changes for FreeBSD package. Thanks, Dan.
- Fix ``ZabbixSender.py``. Thanks, Ben!
- service tweaks: nsca, zabbix


2020-06-06 0.16.2
=================
- Optionally choose scheme for connection to InfluxDB. Thanks, Dennis!


2020-06-06 0.16.1
=================
- Fix charset encoding within pipe module. Thanks, Morten!
- Fix removal of "as_user" option within Slack plugin. Thanks, Morten!


2020-05-30 0.16.0
=================
- Fix for the mqttwarn.service service unit. Thanks, Fulvio!
- Fix encoding of data for Python3 within Pushsafer plugin. Thanks, Thomas!
- Non-JSON payload should not generate warning. Thanks, Morten!
- Fix missing namespace within Serial plugin. Thanks, Morten!
- Fix Dockerfile to use mqttwarn pip module. Thanks, Koen!
- Add Docker Compose file and update Dockerfile to use /etc/mqttwarn. Thanks, Koen!
- Change Dockerfile base image to python:3.8.2-slim-buster. Thanks, Koen!
- Improve code formatting within custom functions of "warntoggle" example. Thanks, Dan!
- Fix charset encoding within Serial plugin. Thanks, Morten!


2020-04-14 0.15.0
=================
- Document ``tls=True`` setting. Thanks, @jpmens!
- Add ``warntoggle`` example (#408). Thanks, @robdejonge!
- Load functions file at configuration load (#410). Thanks, @fhriley!
- Try to make "zabbix" service work again


2020-03-31 0.14.2
=================
- Upgrade to apprise 0.8.5


2020-03-28 0.14.1
=================
- Upgrade xmpppy to 0.6.1, add dnspython as dependency


2020-03-18 0.14.0
=================
- Add service plugin for `Apprise <https://github.com/caronc/apprise>`_.
- Upgrade xmpppy to 0.6.0
- More verbose exception when formatting message fails


2020-03-04 0.13.9
=================
- Remove references to ``mqttwarn.py``. Cleanup documentation.
- Fix charset encoding within Postgres plugin. Thanks, @clarkspark!
- Fix function invocation through "format" setting. Thanks, @clarkspark!


2020-01-12 0.13.8
=================
- Fix charset encoding issue for service "mqttpub". Thanks, @jpmens!


2020-01-12 0.13.7
=================
- Improve exception handling when service plugin fails
- Properly handle charset encoding, both on Python 2 and Python 3


2020-01-09 0.13.6
=================
- Support Python 3.8


2019-12-27 0.13.5
=================
- Improve Python2/3 compatibility for "make-config" subcommand. Fix #393.
  Thanks, @Gulaschcowboy!


2019-12-17 0.13.2
=================
- Fix documentation


2019-12-17 0.13.1
=================
- Address compatibility issues with configparser


2019-12-17 0.13.0
=================
- Remove instapush service as it no longer exists
- Python2/3 compatibility
- Make "pushover" service use requests
- Mitigate some deprecation warnings. Bump core package dependencies.
- Improve testing and CI


2019-12-02 0.12.0
=================
- Add documentation based on Jekyll and publish on www.mqttwarn.net. Thanks, @jpmens!
- Add logo source and PNG images. Thanks, @gumm!
- Make testsuite pass successfully on Python3.
- Make README.rst ASCII-compatible, resolve #386. Thanks, @dlangille!
- Fix direct plugin invocation
- Re-add compatibility with Python2


2019-11-20 0.11.3
=================
- Fix README.rst


2019-11-20 0.11.2
=================
- Remove "Topic :: Internet :: MQTT" from the list of trove classifiers
  after PyPI upload croaked again


2019-11-20 0.11.1
=================
- Update author email within setup.py after PyPI upload croaked at us


2019-11-20 0.11.0
=================
- Add foundation for unit tests based on pytest
- Add test harness
- Integrate changes from the main branch
- Improve documentation, add a more compact ``README.rst`` and
  move the detailed documentation to ``HANDBOOK.md`` for now.
- First release on PyPI


.. _mqttwarn-0.10.1:

2018-04-17 0.10.1
=================
- Use EPL 2.0 license as recently approved by @pypa and @jpmens
- Add missing dependency to the "six" package


.. _mqttwarn-0.10.0:

2018-04-13 0.10.0
=================
- Add mechanism to run a notification service plugin interactively from the command line
- Attempt to fix #307 re. logging to the configuration .ini file. Thanks, Dan!


.. _mqttwarn-0.9.0:

2018-04-13 0.9.0
================
- Add .bumpversion.cfg and Makefile to ease release cutting
- Move "websocket" service plugin (#305) into module namespace
- Refactor two more functions into ``class RuntimeContext``
- Improve error handling: Add the ``exception_traceback()`` primitive to add
  full stacktrace information to log messages. When applied at all important
  places across the board where we do catch-all style exception handling,
  this will improve the experience when working on custom solutions with
  *mqttwarn* to a huge extent.
- Improve documentation


.. _mqttwarn-0.8.1:

2018-04-12 0.8.1
================
- Add required modules for all services to "setup.py"
- Fix setup documentation
- Add MANIFEST.in file


.. _mqttwarn-0.8.0:

2018-04-12 0.8.0
================
- Move all services into module namespace
- Fix PeriodicThread
- Add "requests" module as a core requirement to "setup.py" as it is a common module used by many services
- Add commands "mqttwarn make-config" and "mqttwarn make-samplefuncs"
  for generating a "mqttwarn.ini" or a "samplefuncs.py" file, respectively.
- Add more modules to "extras" requirements section in "setup.py"


.. _mqttwarn-0.7.0:

2018-04-12 0.7.0
================
- Import 0.6.0 code base
- Start work on making mqttwarn a first citizen of the Python ecosystem
- Move main program ``mqttwarn.py`` into module namespace as ``core.py``
- Refactor routines from ``core.py`` into other modules while gently introducing OO
- Add setup.py
- Add full license text
