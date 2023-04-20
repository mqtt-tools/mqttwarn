.. image:: https://github.com/jpmens/mqttwarn/workflows/Tests/badge.svg
    :target: https://github.com/jpmens/mqttwarn/actions?workflow=Tests

.. image:: https://codecov.io/gh/jpmens/mqttwarn/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/jpmens/mqttwarn

.. image:: https://img.shields.io/pypi/pyversions/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/v/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/l/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/status/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://pepy.tech/badge/mqttwarn/month
    :target: https://pepy.tech/project/mqttwarn

.. raw:: html

    <br/><br/>

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

A picture says a thousand words.

.. image:: https://raw.githubusercontent.com/jpmens/mqttwarn/main/assets/mqttwarn.png
    :target: #


Coverage
========

*mqttwarn* comes with **over 70 notification handler plugins** for a wide
range of notification services and is very open to further contributions.
You can enjoy the alphabetical list of plugins at `mqttwarn notification
services`_.

On top of that, it integrates with the excellent `Apprise`_ notification
library. `Apprise notification services`_ has a complete list of the **80+
notification services** supported by Apprise.


Details
=======

The program, running as a service, subscribes to any number of MQTT topics
(including wildcards) and publishes received payloads to one or more notification
services, including support for notifying more than one distinct service
for the same message.

Notifications are transmitted to the appropriate service via plugins.
*mqttwarn* provides built-in plugins for a number of services and you
can easily add your own.

A more detailed blog post about what mqttwarn can be used for is available
at `How do your servers talk to you?`_.

For example, you may wish to submit an alarm published as text to the
MQTT topic ``home/monitoring/+`` as notification via *e-mail* and *Pushover*.



*************
Documentation
*************

The `handbook`_ is the right place to read all about *mqttwarn*'s features and
service plugins.


************
Installation
************

Synopsis::

    pip install --upgrade mqttwarn

You can also add support for a specific service plugin::

    pip install --upgrade 'mqttwarn[xmpp]'

You can also add support for multiple services, all at once::

    pip install --upgrade 'mqttwarn[apprise,asterisk,nsca,desktopnotify,tootpaste,xmpp]'

.. seealso::

   :ref:`using-pip`.


***************
Container image
***************

For running ``mqttwarn`` on a container infrastructure like Docker or
Kubernetes, corresponding images are automatically published to the
GitHub Container Registry (GHCR).

- ``ghcr.io/jpmens/mqttwarn-standard:latest``
- ``ghcr.io/jpmens/mqttwarn-full:latest``

To learn more about this topic, please follow up reading the `Docker handbook`_.


*************
Configuration
*************

.. seealso::

   :ref:`configure`.


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

    # Launch "ntfy" service plugin
    mqttwarn --plugin=ntfy --options='{"addrs": {"url": "http://localhost:5555/testdrive"}, "title": "Example notification", "message": "Hello world"}' --data='{"tags": "foo,bar,äöü", "priority": "high"}'

    # Launch "ntfy" service plugin, and add remote attachment
    mqttwarn --plugin=ntfy --options='{"addrs": {"url": "http://localhost:5555/testdrive"}, "title": "Example notification", "message": "Hello world"}' --data='{"attach": "https://unsplash.com/photos/spdQ1dVuIHw/download?w=320", "filename": "goat.jpg"}'

    # Launch "ntfy" service plugin, and add attachment from local filesystem
    mqttwarn --plugin=ntfy --options='{"addrs": {"url": "http://localhost:5555/testdrive", "attachment": "goat.jpg"}, "title": "Example notification", "message": "Hello world"}'

    # Launch "ssh" service plugin
    mqttwarn --plugin=ssh --config='{"host": "ssh.example.org", "port": 22, "user": "foo", "password": "bar"}' --options='{"addrs": ["command with substitution %s"], "payload": "{\"args\": \"192.168.0.1\"}"}'

    # Launch "cloudflare_zone" service plugin from "mqttwarn-contrib"
    pip install mqttwarn-contrib
    mqttwarn --plugin=mqttwarn_contrib.services.cloudflare_zone --config='{"auth-email": "foo", "auth-key": "bar"}' --options='{"addrs": ["0815", "www.example.org", ""], "message": "192.168.0.1"}'


Also, the ``--config-file`` parameter can be used to optionally specify the
path to a configuration file.


Running as system daemon
========================
- We recommend to use Supervisor_ for running *mqttwarn* as a service, see also `supervisor.ini`_.
- Alternatively, have a look at `mqttwarn.service`_, the systemd unit configuration file for *mqttwarn*.


Running in a development sandbox
================================
For hacking_ on mqttwarn, please install it in development mode.


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
You will need at least the following components:

* Python 3.x or PyPy 3.x.
* An MQTT broker. We recommend Mosquitto_.
* Some more Python modules to satisfy service dependencies defined in the ``setup.py`` file.


Contributing
============
We are always happy to receive code contributions, ideas, suggestions
and problem reports from the community.

So, if you'd like to contribute you're most welcome.
Spend some time taking a look around, locate a bug, design issue or
spelling mistake and then send us a pull request or create an `issue`_.

Thanks in advance for your efforts, we really appreciate any help or feedback.

There are also some extensions to mqttwarn not included in the core package.
Yet, they are bundled into another package, ``mqttwarn-contrib``, see also
`community contributions to mqttwarn`_.


Licenses
========
This software is copyright © 2014-2023 Jan-Piet Mens and contributors. All
rights reserved.

It is and will always be **free and open source software**.

Use of the source code included here is governed by the `Eclipse Public License
2.0 <EPL-2.0_>`_, see LICENSE_ file for details. Please also recognize the
licenses of third-party components.


***************
Troubleshooting
***************
If you encounter any problems during setup or operations or if you have further
suggestions, please let us know by `opening an issue on GitHub`_. Thank you
already.


*************
Miscellaneous
*************


Press
=====
* The article `MQTTwarn: Ein Rundum-Sorglos-Notifier`_ in German at JAXenter.
* The folks of the Berlin-based beekeeper collective Hiveeyes_ are monitoring their beehives and use *mqttwarn*
  as a building block for their alert notification system, enjoy reading `Schwarmalarm using mqttwarn`_.


Legal stuff
===========
"MQTT" is a trademark of the OASIS open standards consortium, which publishes the MQTT specifications.


----

Have fun!


.. _Apprise: https://github.com/caronc/apprise
.. _Apprise notification services: https://github.com/caronc/apprise/wiki#notification-services
.. _backlog: https://github.com/jpmens/mqttwarn/blob/main/doc/backlog.rst
.. _community contributions to mqttwarn: https://pypi.org/project/mqttwarn-contrib/
.. _Docker handbook: https://github.com/jpmens/mqttwarn/blob/main/DOCKER.md
.. _EPL-2.0: https://www.eclipse.org/legal/epl-2.0/
.. _hacking: https://github.com/jpmens/mqttwarn/blob/main/doc/hacking.rst
.. _handbook: https://github.com/jpmens/mqttwarn/blob/main/HANDBOOK.md
.. _Hiveeyes: https://hiveeyes.org/
.. _How do your servers talk to you?: https://jpmens.net/2014/04/03/how-do-your-servers-talk-to-you/
.. _issue: https://github.com/jpmens/mqttwarn/issues/new
.. _LICENSE: https://github.com/jpmens/mqttwarn/blob/main/LICENSE
.. _Mosquitto: https://mosquitto.org
.. _MQTTwarn\: Ein Rundum-Sorglos-Notifier: https://web.archive.org/web/20140611040637/http://jaxenter.de/news/MQTTwarn-Ein-Rundum-Sorglos-Notifier-171312
.. _mqttwarn notification services: https://github.com/jpmens/mqttwarn/blob/main/HANDBOOK.md#supported-notification-services
.. _mqttwarn.service: https://github.com/jpmens/mqttwarn/blob/main/etc/mqttwarn.service
.. _opening an issue on GitHub: https://github.com/jpmens/mqttwarn/issues/new
.. _Schwarmalarm using mqttwarn: https://hiveeyes.org/docs/system/schwarmalarm-mqttwarn.html
.. _Supervisor: https://jpmens.net/2014/02/13/in-my-toolbox-supervisord/
.. _supervisor.ini: https://github.com/jpmens/mqttwarn/blob/main/etc/supervisor.ini
