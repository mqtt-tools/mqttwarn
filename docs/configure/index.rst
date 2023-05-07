.. _configure:

#############
Configuration
#############

This part of the documentation covers the configuration of mqttwarn. The second
step to using any software package after its :ref:`installation <installation>`,
is getting it properly configured. Please read this section carefully.

To directly jump to the corresponding sections, visit
:ref:`mqttwarn.ini`, :ref:`services`, :ref:`topics`, and :ref:`transformations`.


******************************
Application configuration file
******************************

In this section, you will learn about the layout, structure, and semantics of
the application configuration file ``mqttwarn.ini``.
mqttwarn needs it properly configured in order to operate successfully.


Create starter files
====================


Blueprints for mqttwarn configuration files are available within the mqttwarn
repository at `mqttwarn.ini`_ and `udf.py`_. You can use them as personal
starter files, and edit them to your taste::

    # Create configuration file.
    mqttwarn make-config > mqttwarn.ini

    # Create file hosting user-defined functions.
    mqttwarn make-udf > udf.py

.. important::

   If you are using PowerShell on Windows 10, you may find the files to be written
   using the ``UTF-16`` charset encoding. However, ``mqttwarn`` works with ``UTF-8``.
   In order to switch to ``UTF-8``, please invoke this command beforehand.

   .. code-block:: powershell

       $PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'


Learn and edit configuration
============================

In order to implement mqttwarn for your use case, you will need to edit its
configuration files according to your needs.

To learn about the application configuration file ``mqttwarn.ini``, please
follow up reading the following sections of the documentation.

.. toctree::
   :maxdepth: 1

   mqttwarn.ini
   service
   topic
   transformation
   task

Notification "services" define where messages are routed to, "topics" are
definitions of MQTT topic subscriptions, and with "transformations", you are
defining how messages will be filtered, decoded, and re-formatted while
mqttwarn is processing them.


.. _mqttwarn.ini: https://github.com/mqtt-tools/mqttwarn/blob/main/mqttwarn/examples/basic/mqttwarn.ini
.. _udf.py: https://github.com/mqtt-tools/mqttwarn/blob/main/mqttwarn/examples/basic/udf.py
