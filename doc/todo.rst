#############
mqttwarn todo
#############


**********
Essentials
**********
Task: Make mqttwarn a first citizen of the Python ecosystem

- [x] Refactoring. Move "services" into module namespace.
- [x] Put example "mqttwarn.ini" into resources folder of module namespace,
      add "mqttwarn make-config" and "mqttwarn make-samplefuncs"  commands to dump them to stdout
- [x] Add Makefile for releasing and documentation building


*********
Optionals
*********
- [o] Integrate templates into basic example?
- [o] Adapt configuration for Supervisor and systemd
- [o] Move the whole /examples folder into /mqttwarn/examples?
- [o] Where to put /templates and /vendor?
- [o] Check the zabbix and other modules

- [o] How to address "samplefuncs.py" in relation to "mqttwarn.ini"?
- [o] Translate documentation into reStructuredText format, render using Sphinx and publish using readthedocs.org
- [o] Add software tests
- [o] Add Python 3 compatibility
- [o] Improve logging: Let "file" service report about where it's writing to
