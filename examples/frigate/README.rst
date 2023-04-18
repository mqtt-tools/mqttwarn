#################################
Forwarding Frigate events to Ntfy
#################################


*****
About
*****

The specific scenario is to setup a notification pipeline which looks like::

    Frigate -> Mosquitto -> mqttwarn -> Apprise -> Ntfy

`Frigate`_ (`Frigate on GitHub`_) is a network video recorder (NVR) with
realtime local object detection for IP cameras. It uses MQTT to publish
`events in JSON format`_ and `camera pictures in JPEG format`_.

`Apprise`_ is a polyglot notification library that allows you to send
notifications to almost all of the most popular notification services
available today. It has an adapter for `Ntfy`_.

`Ntfy`_ (`Ntfy on GitHub`_) is a simple HTTP-based pub-sub notification
service, allowing you to send notifications to your phone or desktop from
any computer, entirely without signup, cost or setup.


*******
Details
*******

We are investigating how to `Send message body or attachment to Apprise/Ntfy`_,
and if it is feasible to make mqttwarn process JPEG content, see `Non-UTF-8
encoding causes error`_.


*****
Usage
*****

In a box
========

Start the Mosquitto MQTT broker::

    docker run --name=mosquitto --rm -it --publish=1883:1883 \
        eclipse-mosquitto:2.0.15 mosquitto -c /mosquitto-no-auth.conf

Start the Ntfy API service::

    docker run --name=ntfy --rm -it --publish=5555:80 \
        binwiederhier/ntfy serve

Run mqttwarn::

    cd examples/frigate/
    MQTTWARNINI=frigate.ini mqttwarn

Run the example publisher program::

    ./publish.sh

Manually
========

Publish a few example events individually::

    cat frigate-event-new.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    cat frigate-event-end.json | jq -c | mosquitto_pub -t 'frigate/events' -l
    cat frigate-event-false-positive.json | jq -c | mosquitto_pub -t 'frigate/events' -l

Publish an example image::

    wget -O goat.png https://user-images.githubusercontent.com/453543/231550862-5a64ac7c-bdfa-4509-86b8-b1a770899647.png
    convert goat.png goat.jpg
    mosquitto_pub -f goat.jpg -t 'frigate/cam-testdrive/goat/snapshot'
    open /tmp/mqttwarn-frigate-cam-testdrive-goat.jpg


.. _Apprise: https://github.com/caronc/apprise
.. _camera pictures in JPEG format: https://docs.frigate.video/integrations/mqtt/#frigatecamera_nameobject_namesnapshot
.. _events in JSON format: https://docs.frigate.video/integrations/mqtt/#frigateevents
.. _Frigate: https://frigate.video/
.. _Frigate on GitHub: https://github.com/blakeblackshear/frigate
.. _Non-UTF-8 encoding causes error: https://github.com/jpmens/mqttwarn/issues/634
.. _Ntfy: https://ntfy.sh/
.. _Ntfy on GitHub: https://github.com/binwiederhier/ntfy
.. _Send message body or attachment to Apprise/Ntfy: https://github.com/jpmens/mqttwarn/issues/632
