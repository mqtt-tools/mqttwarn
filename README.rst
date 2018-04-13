.. image:: https://img.shields.io/badge/Python-2.7-green.svg
    :target: https://github.com/jpmens/mqttwarn/tree/develop

.. image:: https://img.shields.io/pypi/v/mqttwarn.svg
    :target: #

.. image:: https://img.shields.io/github/tag/jpmens/mqttwarn.svg
    :target: https://github.com/jpmens/mqttwarn/tree/develop

|

.. image:: https://cloud.githubusercontent.com/assets/2345521/6320105/4dd7a826-bade-11e4-9a61-72aa163a40a9.png
    :target: #


########
mqttwarn
########
To *warn*, *alert*, or *notify*.

.. image:: https://raw.githubusercontent.com/jpmens/mqttwarn/develop/assets/google-definition.jpg
    :target: #


****
Note
****
This README is a stub for spawning the revamped documentation of the upcoming mqttwarn 1.0.0,
so it is to be considered as a work in progress. You are welcome to participate!

We outlined the tasks for the next releases at todo_.
They will be progressively transferred into GitHub issues.

.. _todo: https://github.com/jpmens/mqttwarn/blob/develop/doc/todo.rst


*****
About
*****
Short: mqttwarn - subscribe to MQTT topics and notify pluggable services.

Long: mqttwarn subscribes to any number of MQTT topics and publishes received payloads to one or more
notification services after optionally applying sophisticated transformations.


********
Examples
********
- Forward an alarm signal received on the MQTT topic ``home/monitoring/+``
  appropriately to E-Mail and to Pushover.

- Franz jagt im komplett verwahrlosten Taxi quer durch Bayern.


*********************
Notification services
*********************
*mqttwarn* comes with over **70 notification handler plugins** for a wide range
of notification services and is very open to further contributions, enjoy the
`alphabetical list of plugins <https://github.com/jpmens/mqttwarn/blob/develop/README.md>`_.


*****
Setup
*****
Synopsis::

    pip install --upgrade 'https://github.com/jpmens/mqttwarn/archive/develop.tar.gz#egg=mqttwarn[xmpp]'

You can also add support for multiple services, all at once::

    pip install --upgrade 'https://github.com/jpmens/mqttwarn/archive/develop.tar.gz#egg=mqttwarn[asterisk,nsca,osxnotify,tootpaste,xmpp]'


*****
Usage
*****

Running interactively
=====================
First, create configuration and custom Python starter files ``mqttwarn.ini`` and ``samplefuncs.py`` and edit to your taste.
::

    # Create configuration file
    mqttwarn make-config > mqttwarn.ini

    # Create file for custom functions
    mqttwarn make-samplefuncs > samplefuncs.py

Then, just launch ``mqttwarn``::

    # Run mqttwarn
    mqttwarn


To supply a different configuration file, use::

    # Define configuration file
    export MQTTWARNINI=/etc/mqttwarn/acme.ini

    # Run mqttwarn
    mqttwarn


Running notification plugins
============================
For debugging or other purposes, you might want to directly run a notification plugin
without the dispatching and transformation machinery of *mqttwarn*.
We have you covered, just try this to launch the plugin standalone by passing essential information using JSON::

    # Launch "log" service plugin
    mqttwarn --plugin=log --data='{"message": "Hello world", "addrs": ["crit"]}'

    # Launch "file" service plugin
    mqttwarn --plugin=file --data='{"message": "Hello world\n", "addrs": ["/tmp/mqttwarn.err"]}'


Please note this feature is a work in progress, so expect there to be dragons.


Running as system daemon
========================
- I recommend you use Supervisor_ for running this, see also `supervisor.ini`_.
- Alternatively, have a look at `mqttwarn.service`_, the systemd unit configuration file for *mqttwarn*.

.. _Supervisor: https://jpmens.net/2014/02/13/in-my-toolbox-supervisord/
.. _supervisor.ini: https://github.com/jpmens/mqttwarn/blob/master/etc/supervisor.ini
.. _mqttwarn.service: https://github.com/jpmens/mqttwarn/blob/master/etc/mqttwarn.service


Runnin in a development sandbox
===============================
For hacking_ on mqttwarn, please install it in development mode.

.. _hacking: https://github.com/jpmens/mqttwarn/blob/develop/doc/hacking.rst



*******************
Project information
*******************

About
=====
The "mqttwarn" program is released under the Eclipse Public License 2.0,
see LICENSE_ file for details.
Its source code lives on `GitHub <https://github.com/jpmens/mqttwarn>`_ and
the Python package is published to `PyPI <https://pypi.org/project/mqttwarn/>`_.
You might also want to have a look at the `documentation <https://github.com/jpmens/mqttwarn/tree/develop/doc>`_.

The software has been tested on Python 2.7.

If you'd like to contribute you're most welcome!
Spend some time taking a look around, locate a bug, design issue or
spelling mistake and then send us a pull request or create an issue.

Thanks in advance for your efforts, we really appreciate any help or feedback.

.. _LICENSE: https://github.com/jpmens/mqttwarn/blob/develop/LICENSE


Requirements
============
You'll need at least the following components:

* Python 2.x. We tested it with 2.6 and 2.7.
* Some more Python modules defined in the ``setup.py`` file. These will probably get installed automatically.
* An MQTT broker. We recommend Mosquitto_.

.. _Mosquitto: https://mosquitto.org


Notes
=====
"MQTT" is a trademark of the OASIS open standards consortium, which publishes the MQTT specifications.


Press
=====
* The article `MQTTwarn: Ein Rundum-Sorglos-Notifier`_ in German at JAXenter.
* The folks of the Berlin-based beekeeper collective Hiveeyes_ are monitoring their beehives and use *mqttwarn*
  as a building block for their alert notification system, enjoy reading `Schwarmalarm using mqttwarn`_.

.. _MQTTwarn\: Ein Rundum-Sorglos-Notifier: https://jaxenter.de/news/MQTTwarn-Ein-Rundum-Sorglos-Notifier-171312
.. _Hiveeyes: https://hiveeyes.org/
.. _Schwarmalarm using mqttwarn: https://hiveeyes.org/docs/system/schwarmalarm-mqttwarn.html


----

Have fun!
