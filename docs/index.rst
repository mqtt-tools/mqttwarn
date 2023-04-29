.. mqttwarn documentation master file, created by
   sphinx-quickstart on Thu Apr 13 05:56:36 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

########
mqttwarn
########

To *warn*, *alert*, or *notify*.

.. image:: assets/google-definition.jpg
   :target: #


*****
About
*****

*mqttwarn - subscribe to MQTT topics and notify pluggable services.*

.. image:: assets/mqttwarn.png
   :target: #

*mqttwarn* is a highly configurable MQTT message router, where the routing targets
are notification plugins, primarily written in Python. A picture says a thousand words.


********
Features
********

- mqttwarn subscribes to any number of MQTT topics, optionally including wildcards,
  and publishes received payloads to one or more notification :ref:`services <services>`,
  after optionally applying sophisticated transformations.
- Notifications are transmitted to notification services via plugins. mqttwarn
  ships with a number of notifier plugins, see :ref:`notification-services`,
  and you can easily add your own.
- For linking MQTT :ref:`topics <topics>` with notification plugins, you will configure
  corresponding mappings within mqttwarn's configuration file ``mqttwarn.ini``.
  You can accomplish, for example, the following mappings:

  * PUBs to ``owntracks/jane/iphone`` should be notified via Pushover to John's phone
  * PUBs to ``openhab/temperature`` should notify Mastodon or Twitter
  * PUBs to ``home/monitoring/alert/+`` should notify Prowl and Mail
- You can optionally engage a sophisticated :ref:`transformation <transformations>` facility.


.. _coverage:

*****************************
Notification service coverage
*****************************

*mqttwarn* comes with **over 70 notification handler plugins** for a wide
range of notification services and is very open to further contributions.
You can enjoy the alphabetical list of plugins at :ref:`notification-services`.

On top of that, *mqttwarn* integrates with the `Apprise`_ notification library.
`Apprise notification services`_ has a complete list of the **80+
notification services** supported by Apprise.


*************
Documentation
*************

In order to configure and operate mqttwarn successfully, please read the
documentation carefully.

- :ref:`Install and operate mqttwarn <use>`
- :ref:`The mqttwarn configuration <configure>`
- :doc:`README <readme>`


.. important::

   mqttwarn aims to provide concise documentation about its machinery and internals.
   If you observe any rough edges, please don't hesitate to submit a suggestion
   how we can improve or extend the documentation. Did we say that we also *love*
   pull requests in this regard?


********
Articles
********

What others are saying about mqttwarn, or what they are using it for.

- `JP`_ has written a few introductory articles. Thanks!

  - `Introducing mqttwarn\: a pluggable MQTT notifier`_
  - `How do your servers talk to you?`_
  - `Alerting or notifying on SSH logins`_
- `MQTTwarn\: Ein Rundum-Sorglos-Notifier`_ article in German at JAXenter.
- The folks of the Berlin-based beekeeper collective `Hiveeyes`_ are monitoring
  their beehives and use *mqttwarn* as a building block for their alert
  notification system, enjoy reading `Schwarmalarm using mqttwarn`_.


*****
Notes
*****

"MQTT" is a trademark of the "OASIS open standards" consortium, which publishes
the MQTT specifications.

----

.. toctree::
   :maxdepth: 2
   :caption: Handbook
   :hidden:

   usage/index
   configure/index
   notifier-catalog
   README <readme>

.. toctree::
   :maxdepth: 2
   :caption: Learn
   :hidden:

   examples/readme

.. toctree::
   :maxdepth: 2
   :caption: Workbench
   :hidden:

   Sandbox <workbench/sandbox>
   Changelog <workbench/changelog>
   Backlog <workbench/backlog>


.. hidden

   Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`



.. _Alerting or notifying on SSH logins: https://jpmens.net/2018/03/25/alerting-on-ssh-logins/
.. _Apprise: https://github.com/caronc/apprise
.. _Apprise notification services: https://github.com/caronc/apprise/wiki#notification-services
.. _Hiveeyes: https://hiveeyes.org/
.. _How do your servers talk to you?: https://jpmens.net/2014/04/03/how-do-your-servers-talk-to-you/
.. _Introducing mqttwarn\: a pluggable MQTT notifier: https://jpmens.net/2014/02/17/introducing-mqttwarn-a-pluggable-mqtt-notifier/
.. _JP: https://jpmens.net/pages/about/
.. _MQTTwarn\: Ein Rundum-Sorglos-Notifier: https://web.archive.org/web/20140611040637/http://jaxenter.de/news/MQTTwarn-Ein-Rundum-Sorglos-Notifier-171312
.. _Schwarmalarm using mqttwarn: https://hiveeyes.org/docs/system/schwarmalarm-mqttwarn.html
