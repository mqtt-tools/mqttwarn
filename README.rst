########
mqttwarn
########
mqttwarn - subscribe to MQTT topics and notify pluggable services.


*****
About
*****
mqttwarn subscribes to any number of MQTT topics and publishes received payloads to one or more
notification services after optionally applying sophisticated transformations.

*****
Setup
*****

Development
===========
Get hold of the sources::

    git clone https://github.com/jpmens/mqttwarn
    cd mqttwarn
    git checkout develop

Create virtualenv and install mqttwarn in development mode::

    virtualenv .venv27
    source .venv27/bin/activate
    python setup.py develop


Production
==========
Todo::

    pip install --upgrade --editable https://github.com/jpmens/mqttwarn/archive/develop.tar.gz [xmpp]
    pip install --upgrade --find-links https://github.com/jpmens/mqttwarn/archive/develop.tar.gz mqttwarn[xmpp]


*****
Usage
*****
::

    export MQTTWARNINI=mqttwarn.ini.sample
    mqttwarn

