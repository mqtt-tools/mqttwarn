##################
mqttwarn changelog
##################


in progress
===========
- Add .bumpversion.cfg and Makefile to ease release cutting


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
