##################
mqttwarn changelog
##################


in progress
===========
- Move all services into module namespace
- Fix PeriodicThread
- Add "requests" module as a core requirement to "setup.py" as it is a common module used by many services
- Add commands "mqttwarn make-config" and "mqttwarn make-samplefuncs"
  for generating a mqttwarn.ini or a samplefuncs.py, respectively.
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
