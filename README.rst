########
mqttwarn
########

.. image:: https://cloud.githubusercontent.com/assets/2345521/6320105/4dd7a826-bade-11e4-9a61-72aa163a40a9.png

To *warn*, *alert*, or *notify*.

.. image:: https://raw.githubusercontent.com/mqtt-tools/mqttwarn/main/assets/google-definition.jpg


******
Status
******

.. image:: https://github.com/mqtt-tools/mqttwarn/workflows/Tests/badge.svg
    :target: https://github.com/mqtt-tools/mqttwarn/actions?workflow=Tests

.. image:: https://codecov.io/gh/mqtt-tools/mqttwarn/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/mqtt-tools/mqttwarn

.. image:: https://img.shields.io/pypi/pyversions/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

|

.. image:: https://img.shields.io/pypi/l/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/status/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://img.shields.io/pypi/v/mqttwarn.svg
    :target: https://pypi.org/project/mqttwarn/

.. image:: https://pepy.tech/badge/mqttwarn/month
    :target: https://pepy.tech/project/mqttwarn

|

`GitHub <https://github.com/mqtt-tools/mqttwarn>`_
| `PyPI <https://pypi.org/project/mqttwarn/>`_
| `Documentation <https://mqttwarn.readthedocs.io>`_
| `Issues <https://github.com/mqtt-tools/mqttwarn/issues>`_
| `Changelog <https://github.com/mqtt-tools/mqttwarn/blob/main/CHANGES.rst>`_


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

.. image:: https://raw.githubusercontent.com/mqtt-tools/mqttwarn/main/assets/mqttwarn.png
    :target: #


Notification service coverage
=============================

*mqttwarn* comes with **over 70 notification handler plugins**, covering a
wide range of notification services and is very open to further contributions.
You can enjoy the alphabetical list of plugins on the `mqttwarn notifier
catalog`_ page.

On top of that, it integrates with the excellent `Apprise`_ notification
library. `Apprise notification services`_ has a complete list of the **80+
notification services** supported by Apprise.



*************
Documentation
*************

The `mqttwarn documentation`_ is the right place to read all about *mqttwarn*'s
features and integrations, and how you can leverage all its framework components
for building custom applications. Its service plugins can be inspected on the
`mqttwarn notifier catalog`_ page.


************
Installation
************

Using pip
=========

Synopsis::

    pip install --upgrade mqttwarn

You can also add support for a specific service plugin::

    pip install --upgrade 'mqttwarn[xmpp]'

You can also add support for multiple services, all at once::

    pip install --upgrade 'mqttwarn[apprise,asterisk,nsca,desktopnotify,tootpaste,xmpp]'

See also: `Installing mqttwarn with pip`_.

OCI container image
===================

For running ``mqttwarn`` on a container infrastructure like Docker or
Kubernetes, corresponding images are automatically published to the
GitHub Container Registry (GHCR).

- ``ghcr.io/mqtt-tools/mqttwarn-standard:latest``
- ``ghcr.io/mqtt-tools/mqttwarn-full:latest``

To learn more about this topic, please follow up reading the `Using the OCI image
with Docker or Podman`_ documentation section.


*************
Configuration
*************

In order to learn how to configure mqttwarn, please head over to the documentation
section about the `mqttwarn configuration`_.


*****
Usage
*****

Interactive service
===================
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

System daemon
=============

There are different ways to run mqttwarn as a system daemon. There are examples
for systemd, traditional init, OpenRC, and Supervisor_ in the ``etc`` directory
of this repository, for example `supervisor.ini`_ (Supervisor) and
`mqttwarn.service`_ (systemd).

Standalone
==========

In order to directly invoke notification plugins from custom programs, or for
debugging them, see `Running notification plugins standalone`_.

Development sandbox
===================

For hacking on mqttwarn, please install it in development mode, using a
`mqttwarn development sandbox`_ installation.


*******************
Project information
*******************

About
=====
These links will guide you to the source code of *mqttwarn* and its documentation.

- `mqttwarn on GitHub <https://github.com/mqtt-tools/mqttwarn>`_
- `mqttwarn on the Python Package Index (PyPI) <https://pypi.org/project/mqttwarn/>`_
- `mqttwarn documentation <https://mqttwarn.readthedocs.io/>`_


Requirements
============
You will need at least the following components:

* Python 3.x or PyPy 3.x.
* An MQTT broker. We recommend `Eclipse Mosquitto`_.
* For invoking specific service plugins, additional Python modules may be required.
  See ``setup.py`` file.


Contributing
============

We are always happy to receive code contributions, ideas, suggestions
and problem reports from the community.

So, if you would like to contribute, you are most welcome.
Spend some time taking a look around, locate a bug, design issue or
spelling mistake, and then send us a pull request or create an `issue`_.

Thank you in advance for your efforts, we really appreciate any help or feedback.


License
=======

mqttwarn is copyright © 2014-2023 Jan-Piet Mens and contributors. All
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


************
Attributions
************

Acknowledgements
================
Thanks to all the contributors of *mqttwarn* who helped to conceive it in one
way or another. You know who you are.

Legal stuff
===========
"MQTT" is a trademark of the OASIS open standards consortium, which publishes the
MQTT specifications. "Eclipse Mosquitto" is a trademark of the Eclipse Foundation.

----

Have fun!


.. _Apprise: https://github.com/caronc/apprise
.. _Apprise notification services: https://github.com/caronc/apprise/wiki#notification-services
.. _backlog: https://github.com/mqtt-tools/mqttwarn/blob/main/doc/backlog.rst
.. _Eclipse Mosquitto: https://mosquitto.org
.. _EPL-2.0: https://www.eclipse.org/legal/epl-2.0/
.. _hacking: https://github.com/mqtt-tools/mqttwarn/blob/main/doc/hacking.rst
.. _How do your servers talk to you?: https://jpmens.net/2014/04/03/how-do-your-servers-talk-to-you/
.. _Installing mqttwarn with pip: https://mqttwarn.readthedocs.io/en/latest/usage/pip.html
.. _issue: https://github.com/mqtt-tools/mqttwarn/issues/new
.. _LICENSE: https://github.com/mqtt-tools/mqttwarn/blob/main/LICENSE
.. _MQTTwarn\: Ein Rundum-Sorglos-Notifier: https://web.archive.org/web/20140611040637/http://jaxenter.de/news/MQTTwarn-Ein-Rundum-Sorglos-Notifier-171312
.. _mqttwarn configuration: https://mqttwarn.readthedocs.io/en/latest/configure/
.. _mqttwarn development sandbox: https://mqttwarn.readthedocs.io/en/latest/workbench/sandbox.html
.. _mqttwarn documentation: https://mqttwarn.readthedocs.io/
.. _mqttwarn notifier catalog: https://mqttwarn.readthedocs.io/en/latest/notifier-catalog.html
.. _mqttwarn.service: https://github.com/mqtt-tools/mqttwarn/blob/main/etc/mqttwarn.service
.. _opening an issue on GitHub: https://github.com/mqtt-tools/mqttwarn/issues/new
.. _Running notification plugins standalone: https://mqttwarn.readthedocs.io/en/latest/usage/standalone.html
.. _Schwarmalarm using mqttwarn: https://hiveeyes.org/docs/system/schwarmalarm-mqttwarn.html
.. _Supervisor: https://jpmens.net/2014/02/13/in-my-toolbox-supervisord/
.. _supervisor.ini: https://github.com/mqtt-tools/mqttwarn/blob/main/etc/supervisor.ini
.. _Using the OCI image with Docker or Podman: https://mqttwarn.readthedocs.io/en/latest/usage/oci.html
