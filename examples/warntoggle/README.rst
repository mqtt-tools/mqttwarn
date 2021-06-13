**********
warntoggle
**********

A custom function to be used when configuring streams in ``mqttwarn``, ``warntoggle`` makes it easy to toggle notifications on or off through a simple web interface.

Example workflow
================

- ``mqttwarn.ini`` has a section ``[+/temperature]``, which applies to all MQTT messages received on matching topics. This section includes a filter, referring to our custom function.
- When an MQTT message is received, the custom function is triggered.
- This custom function checks a JSON file for the topic, and based on ``TRUE`` or ``FALSE`` setting will return a message back to `mqttwarn` to either allow the notification to happen or not.
- If an MQTT topic was not found in aforementioned JSON file, it will be added and set with a configurable default value.
- For the user, an accompanying web script allows the toggle to be changed.

Installation
============

- Copy the ``togglestate()`` function from ``mqttwarn/customfunctions.py`` to your own custom functions file, or copy the entire file and refer to it in `mqttwarn.ini` with a  ``functions = 'customfunctions.py'`` directive.
- Copy the content of the `www` folder to a web server on the same host as `mqttwarn`, ensure Python is enabled for the server and ``warntoggle.json`` is writeable by the web server.
- Create a symbolic link from ``/etc/mqttwarn/warntoggle.json`` -> ``/var/www/html/warntoggle.json`, obviously adjusted for your local situation. Alternatively, configure the filename inside the custom function where it now says ``filename = "warntoggle.js"`` to contain an absolute path.
- For each stream you wish to be considered by ``warntoggle``, add a line ``filter = togglestate()`` to ``mqttwarn.ini``. This must be done inside each stream section.
