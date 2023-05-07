.. _processing-frigate-events:

##############################################
Frigate » Forward events and snapshots to ntfy
##############################################


*****
About
*****

This tutorial presents a notification pipeline, which implements forwarding
Frigate events to ntfy notifications, using mqttwarn. It looks like this::

    Frigate -> Mosquitto -> mqttwarn -> ntfy

Components
==========

`Frigate`_ (`Frigate on GitHub`_) is a network video recorder (NVR) with
realtime local object detection for IP cameras. It uses MQTT to publish
`events in JSON format`_ and `camera pictures in JPEG format`_.

`Eclipse Mosquitto`_ (`Mosquitto on GitHub`_) is an open source message broker
that implements the MQTT protocol versions 5.0, 3.1.1 and 3.1. Mosquitto is
lightweight and is suitable for use on all devices from low power single board
computers to full servers.

`mqttwarn`_ (`mqttwarn on GitHub`_) is a highly configurable MQTT message router,
where the routing targets are notification plugins, written in Python. mqttwarn
has a corresponding notification plugin adapter for ntfy.

`ntfy`_ (`ntfy on GitHub`_) is a simple HTTP-based `pub-sub`_ notification
service, allowing you to send notifications to your phone or desktop from
any computer, entirely without signup, cost or setup.


********
Synopsis
********

1. Publish Frigate sample events.

.. code-block:: bash

    cat assets/frigate-event-new-good.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    mosquitto_pub -f goat.png -t 'frigate/cam-testdrive/goat/snapshot'

2. Enjoy the outcome.

.. figure:: https://user-images.githubusercontent.com/453543/233172276-6a59cefa-6461-48bc-80f2-c355b6acc496.png



*****
Usage
*****


Configuration
=============

Please inspect the `frigate.ini`_ mqttwarn configuration file and adjust it to
your needs before running mqttwarn on it. If you also want to inspect the
corresponding user-defined functions, you are most welcome. They are stored
within `frigate.py`_.

Prerequisites
=============

Acquire sources and go to the right directory::

    git clone https://github.com/mqtt-tools/mqttwarn
    cd mqttwarn/examples/frigate


In a box
========

Start the Mosquitto MQTT broker and the ntfy service::

    docker compose up

Subscribe to ntfy topic by visiting http://localhost:5555/frigate-testdrive.

Run mqttwarn::

    MQTTWARNINI=frigate.ini mqttwarn

Run the example publisher program::

    ./publish.sh

Manually
========

Publish a few example events individually::

    cat assets/frigate-event-new-good.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    cat assets/frigate-event-end.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    cat assets/frigate-event-false-positive.json | jq -c | mosquitto_pub -t 'frigate/events' -l

Publish an example image::

    wget -O goat.png https://user-images.githubusercontent.com/453543/231550862-5a64ac7c-bdfa-4509-86b8-b1a770899647.png
    mosquitto_pub -f goat.png -t 'frigate/cam-testdrive/goat/snapshot'
    open /tmp/mqttwarn-frigate-cam-testdrive-goat.png


*******
Details
*******

The implementation is based on mqttwarn core, its `ntfy service plugin`_, the
mqttwarn configuration file ``frigate.ini``, as well as the user-defined function
file ``frigate.py``. You can inspect them below.

.. admonition:: Inspect configuration file ``frigate.ini``
    :class: tip dropdown

    .. literalinclude:: frigate.ini
       :language: ini

.. admonition:: Inspect user-defined function file ``frigate.py``
    :class: tip dropdown

    .. literalinclude:: frigate.py
       :language: python


*****
Tests
*****

The `test_frigate.py`_ file covers different code paths by running a few Frigate event
message samples through the machinery, and inspecting their outcomes. You can invoke
the test cases either as part of the complete test suite, or by running them from this
directory::

    pytest --no-cov -k frigate
    pytest --no-cov test_frigate.py


************
Attributions
************

Acknowledgements
================
- `Sev`_ for coming up with the idea of using mqttwarn to connect Frigate with ntfy
- `Blake Blackshear`_ for `Frigate`_
- `Philipp C. Heckel`_ for `ntfy`_

Content
=======
The copyright of data, particular images, and pictograms, are held by their
respective owners, unless otherwise noted.

Example snapshot image
----------------------

- **Description**:  A picture of a `Changthangi`_ goat
- **Date**:         April 7, 2023
- **Source**:       Own work via Unsplash
- **Author**:       `Jaromír Kalina`_
- **License**:      `Unsplash License`_
- **URL**:          https://unsplash.com/photos/spdQ1dVuIHw


.. _Blake Blackshear: https://github.com/blakeblackshear
.. _camera pictures in JPEG format: https://docs.frigate.video/integrations/mqtt/#frigatecamera_nameobject_namesnapshot
.. _Changthangi: https://en.wikipedia.org/wiki/Changthangi
.. _Eclipse Mosquitto: https://mosquitto.org/
.. _events in JSON format: https://docs.frigate.video/integrations/mqtt/#frigateevents
.. _Frigate: https://frigate.video/
.. _Frigate on GitHub: https://github.com/blakeblackshear/frigate
.. _frigate.ini: https://github.com/mqtt-tools/mqttwarn/blob/main/examples/frigate/frigate.ini
.. _frigate.py: https://github.com/mqtt-tools/mqttwarn/blob/main/examples/frigate/frigate.py
.. _Jaromír Kalina: https://unsplash.com/@jkalinaofficial
.. _Mosquitto on GitHub: https://github.com/eclipse/mosquitto
.. _mqttwarn: https://mqttwarn.readthedocs.io/
.. _mqttwarn on GitHub: https://github.com/mqtt-tools/mqttwarn
.. _ntfy: https://ntfy.sh/
.. _ntfy on GitHub: https://github.com/binwiederhier/ntfy
.. _ntfy service plugin: https://mqttwarn.readthedocs.io/en/latest/notifier-catalog.html#ntfy
.. _Philipp C. Heckel: https://github.com/binwiederhier
.. _pub-sub: https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern
.. _Sev: https://github.com/sevmonster
.. _test_frigate.py: https://github.com/mqtt-tools/mqttwarn/blob/main/examples/frigate/test_frigate.py
.. _Unsplash License: https://unsplash.com/license
