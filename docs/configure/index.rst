.. _configure:

#############
Configuration
#############

This part of the documentation covers the configuration of mqttwarn. The second
step to using any software package after installation is getting it properly
configured. Please read this section carefully.

After successfully installing the software, you might want to follow up about
:ref:`using <using>` it.


******************************
Application configuration file
******************************

Create starter files
====================

Blueprints of configuration files for running mqttwarn in development and
production mode are available within the mqttwarn repository.

First, create configuration and custom Python starter files ``mqttwarn.ini``
and ``samplefuncs.py`` and edit them to your taste::

    # Create configuration file
    mqttwarn make-config > mqttwarn.ini

    # Create file for custom functions
    mqttwarn make-samplefuncs > samplefuncs.py

.. important::

   If you are using PowerShell on Windows 10, you may find the files to be written
   using the ``UTF-16`` charset encoding. However, ``mqttwarn`` works with ``UTF-8``.
   In order to switch to ``UTF-8``, please invoke this command beforehand.

   .. code-block:: powershell

       $PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'


Edit starter files
==================

In order to learn about the structure of the application configuration file
``mqttwarn.ini``, please follow up reading the following sections of the
documentation.

.. toctree::
   :maxdepth: 2

   service
   topic


