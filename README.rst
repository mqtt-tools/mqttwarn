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
Synopsis::

    pip install --upgrade 'https://github.com/jpmens/mqttwarn/archive/develop.tar.gz' mqttwarn[xmpp]


*****
Usage
*****
::

    # Create configuration file
    mqttwarn make-config > mqttwarn.ini

    # Create file for custom functions
    mqttwarn make-samplefuncs > samplefuncs.py

    # Run mqttwarn
    mqttwarn


To supply a different configuration file, use::

    # Define configuration file
    export MQTTWARNINI=mqttwarn.ini.sample

    # Run mqttwarn
    mqttwarn
