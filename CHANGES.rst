##################
mqttwarn changelog
##################


in progress
===========


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
- Integrate changes from the master branch
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
