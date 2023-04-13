.. mqttwarn documentation master file, created by
   sphinx-quickstart on Thu Apr 13 05:56:36 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

########
mqttwarn
########


*****
About
*****

*mqttwarn - subscribe to MQTT topics and notify pluggable services.*

*mqttwarn* subscribes to any number of MQTT topics and publishes received
payloads to one or more notification services after optionally applying
sophisticated transformations.

A picture says a thousand words.

.. image:: https://raw.githubusercontent.com/jpmens/mqttwarn/main/assets/mqttwarn.png
    :target: #


********
Coverage
********

*mqttwarn* comes with **over 70 notification handler plugins** for a wide
range of notification services and is very open to further contributions.
You can enjoy the alphabetical list of plugins at `mqttwarn notification
services`_.

On top of that, it integrates with the `Apprise`_ notification library.
`Apprise notification services`_ has a complete list of the **80+
notification services** supported by Apprise.


*************
Documentation
*************

Please follow up reading the :doc:`README <readme>` and :doc:`handbook
<handbook>`. That's all we have.

The authors of mqttwarn aim to provide good documentation about its
machinery and internals. However, mqttwarn includes a complex set of
transformation capabilities, which is sometimes not easy to understand.

So, if you observe any rough edges, please don't hesitate to submit a
suggestion how we can improve the documentation.


----

.. toctree::
   :maxdepth: 1
   :caption: Overview
   :hidden:

   README <readme>
   HANDBOOK <handbook>

.. toctree::
   :maxdepth: 2
   :caption: Details
   :hidden:

   usage/oci
   configure/index
.. toctree::
   :maxdepth: 2
   :caption: Tutorials
   :hidden:

   tutorial/frigate/README
   tutorial/warntoggle/README

.. toctree::
   :maxdepth: 2
   :caption: Workbench
   :hidden:

   Development sandbox <workbench/sandbox>
   Changelog <workbench/changelog>
   Backlog <workbench/backlog>


.. hidden

   Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`



.. _Apprise: https://github.com/caronc/apprise
.. _Apprise notification services: https://github.com/caronc/apprise/wiki#notification-services
.. _mqttwarn notification services: https://github.com/jpmens/mqttwarn/blob/main/HANDBOOK.md#supported-notification-services
