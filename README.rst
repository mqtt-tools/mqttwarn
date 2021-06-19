.. image:: https://github.com/jpmens/mqttwarn/workflows/Tests/badge.svg
    :target: https://github.com/jpmens/mqttwarn/actions?workflow=Tests

.. image:: https://codecov.io/gh/jpmens/mqttwarn/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/jpmens/mqttwarn

.. image:: https://img.shields.io/pypi/pyversions/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/v/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/l/mqttwarn.svg
    :alt: License
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/status/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

|

.. image:: https://cloud.githubusercontent.com/assets/2345521/6320105/4dd7a826-bade-11e4-9a61-72aa163a40a9.png


########
mqttwarn
########

To *warn*, *alert*, or *notify*.

.. image:: https://raw.githubusercontent.com/jpmens/mqttwarn/main/assets/google-definition.jpg



*****
About
*****

mqttwarn - subscribe to MQTT topics and notify pluggable services.


Description
===========
*mqttwarn* subscribes to any number of MQTT topics and publishes received
payloads to one or more notification services after optionally applying
sophisticated transformations.

It comes with over **70 notification handler plugins** for a wide
range of notification services and is very open to further contributions.
You can enjoy the alphabetical list of plugins within the handbook_services_.

A picture says a thousand words.

.. image:: https://raw.githubusercontent.com/jpmens/mqttwarn/main/assets/mqttwarn.png
    :target: #


Introduction
============
This program subscribes to any number of MQTT topics (which may include
wildcards) and publishes received payloads to one or more notification
services, including support for notifying more than one distinct service
for the same message.

Notifications are transmitted to the appropriate service via plugins.
*mqttwarn* provides built-in plugins for a number of services and you
can easily add your own.

A more detailed blog post about what mqttwarn can be used for is available
at https://jpmens.net/2014/04/03/how-do-your-servers-talk-to-you/.

For example, you may wish to submit an alarm published as text to the
MQTT topic ``home/monitoring/+`` as notification via *e-mail* and *Pushover*.


.. _handbook: https://github.com/jpmens/mqttwarn/blob/main/HANDBOOK.md
.. _Docker handbook: https://github.com/jpmens/mqttwarn/blob/main/DOCKER.md
.. _handbook_services: https://github.com/jpmens/mqttwarn/blob/main/HANDBOOK.md#supported-notification-services


*************
Documentation
*************

The handbook_ is the right place to read all about *mqttwarn*'s
features and service plugins.


************
Installation
************

Synopsis::

    pip install --upgrade mqttwarn

You can also add support for a specific service plugin::

    pip install --upgrade 'mqttwarn[xmpp]'

You can also add support for multiple services, all at once::

    pip install --upgrade 'mqttwarn[apprise,asterisk,nsca,osxnotify,tootpaste,xmpp]'


***************
Container image
***************

For running ``mqttwarn`` on a container infrastructure like Docker or
Kubernetes, there are images on Docker Hub called ``jpmens/mqttwarn``.
To read more about this topic, please follow up on the `Docker handbook`_.


*************
Configuration
*************

First, create configuration and custom Python starter files
``mqttwarn.ini`` and ``samplefuncs.py`` and edit them to your taste::

    # Create configuration file
    mqttwarn make-config > mqttwarn.ini

    # Create file for custom functions
    mqttwarn make-samplefuncs > samplefuncs.py


*****
Usage
*****

Running interactively
=====================
Just launch ``mqttwarn``::

    # Run mqttwarn
    mqttwarn


To supply a different configuration file or log file, optionally use::

    # Define configuration file
    export MQTTWARNINI=/etc/mqttwarn/acme.ini

    # Define log file
    export MQTTWARNLOG=/var/log/mqttwarn.log

    # Run mqttwarn
    mqttwarn


Running notification plugins
============================
For debugging, or other purposes, you might want to directly run an individual
notification plugin without the dispatching and transformation machinery of
*mqttwarn*.

We have you covered. To launch a plugin standalone, those commands will give
you an idea how to pass relevant information on the command line using JSON::

    # Launch "log" service plugin
    mqttwarn --plugin=log --options='{"message": "Hello world", "addrs": ["crit"]}'

    # Launch "file" service plugin
    mqttwarn --plugin=file --options='{"message": "Hello world\n", "addrs": ["/tmp/mqttwarn.err"]}'

    # Launch "pushover" service plugin
    mqttwarn --plugin=pushover --options='{"title": "About", "message": "Hello world", "addrs": ["userkey", "token"], "priority": 6}'

    # Launch "ssh" service plugin from the command line
    mqttwarn --plugin=ssh --config='{"host": "ssh.example.org", "port": 22, "user": "foo", "password": "bar"}' --options='{"addrs": ["command with substitution %s"], "payload": "{\"args\": \"192.168.0.1\"}"}'

    # Launch "cloudflare_zone" service plugin from "mqttwarn-contrib", passing "--config" parameters via command line
    pip install mqttwarn-contrib
    mqttwarn --plugin=mqttwarn_contrib.services.cloudflare_zone --config='{"auth-email": "foo", "auth-key": "bar"}' --options='{"addrs": ["0815", "www.example.org", ""], "message": "192.168.0.1"}'


Also, the ``--config-file`` parameter can be used to optionally specify the
path to a configuration file.


Running as system daemon
========================
- We recommend to use Supervisor_ for running *mqttwarn* as a service, see also `supervisor.ini`_.
- Alternatively, have a look at `mqttwarn.service`_, the systemd unit configuration file for *mqttwarn*.

.. _Supervisor: https://jpmens.net/2014/02/13/in-my-toolbox-supervisord/
.. _supervisor.ini: https://github.com/jpmens/mqttwarn/blob/main/etc/supervisor.ini
.. _mqttwarn.service: https://github.com/jpmens/mqttwarn/blob/main/etc/mqttwarn.service


Running in a development sandbox
================================
For hacking_ on mqttwarn, please install it in development mode.

.. _hacking: https://github.com/jpmens/mqttwarn/blob/main/doc/hacking.rst



****************
Acknowledgements
****************
Thanks to all the contributors of *mqttwarn* who got their hands dirty with it
and helped to co-create and conceive it in one way or another. You know who you are.


*******************
Project information
*******************

About
=====
These links will guide you to the source code of *mqttwarn* and its documentation.

- `mqttwarn on GitHub <https://github.com/jpmens/mqttwarn>`_
- `mqttwarn on the Python Package Index (PyPI) <https://pypi.org/project/mqttwarn/>`_
- `mqttwarn documentation <https://github.com/jpmens/mqttwarn/tree/main/doc>`_


Requirements
============
You'll need at least the following components:

* Python. The program should work on Python 3 and PyPy3.
* An MQTT broker. We recommend Mosquitto_.
* Some more Python modules to satisfy service dependencies defined in the ``setup.py`` file.

.. _Mosquitto: https://mosquitto.org


Contributing
============
We are always happy to receive code contributions, ideas, suggestions
and problem reports from the community.

So, if you'd like to contribute you're most welcome.
Spend some time taking a look around, locate a bug, design issue or
spelling mistake and then send us a pull request or create an issue_.

Thanks in advance for your efforts, we really appreciate any help or feedback.


Licenses
========
This software is copyright © 2014-2019 Jan-Piet Mens and contributors. All rights reserved.

It is and will always be **free and open source software**.

Use of the source code included here is governed by the
`Eclipse Public License 2.0 <EPL-2.0_>`_, see LICENSE_ file for details.
Please also recognize the licenses of third-party components.

.. _issue: https://github.com/jpmens/mqttwarn/issues/new
.. _EPL-2.0: https://www.eclipse.org/legal/epl-2.0/
.. _LICENSE: https://github.com/jpmens/mqttwarn/blob/main/LICENSE


***************
Troubleshooting
***************
If you encounter any problems during setup or operations or if you have further
suggestions, please let us know by `opening an issue on GitHub <issue_>`_.
Thanks already.


*************
Miscellaneous
*************


Press
=====
* The article `MQTTwarn: Ein Rundum-Sorglos-Notifier`_ in German at JAXenter.
* The folks of the Berlin-based beekeeper collective Hiveeyes_ are monitoring their beehives and use *mqttwarn*
  as a building block for their alert notification system, enjoy reading `Schwarmalarm using mqttwarn`_.

.. _MQTTwarn\: Ein Rundum-Sorglos-Notifier: https://jaxenter.de/news/MQTTwarn-Ein-Rundum-Sorglos-Notifier-171312
.. _Hiveeyes: https://hiveeyes.org/
.. _Schwarmalarm using mqttwarn: https://hiveeyes.org/docs/system/schwarmalarm-mqttwarn.html


Notes
=====
*mqttwarn* is currently undergoing some refurbishment and will also be
ported to Python 3 during that phase. You are welcome to participate!

We outlined the tasks for the next releases within the backlog_.
They might be transferred into GitHub issues progressively, if applicable.

.. _backlog: https://github.com/jpmens/mqttwarn/blob/main/doc/backlog.rst


Legal stuff
===========
"MQTT" is a trademark of the OASIS open standards consortium, which publishes the MQTT specifications.


----

Have fun!
