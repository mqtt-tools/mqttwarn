.. _installation:
.. _installing:
.. _install:
.. _usage:
.. _using:
.. _use:

######################
Installation and usage
######################

This part of the documentation covers the installation and usage of mqttwarn.
The first step to using any software package is getting it properly installed.
Please read this section carefully.

After successfully installing the software, please follow up to learn about how
to :ref:`configure <configure>` it.

Installation variants
=====================

mqttwarn can be installed natively on your system, or by running an OCI container
image on Docker, Podman, Kubernetes, or friends. Depending on your preferences or
system environment, please use either of those variants:

- :ref:`using-pip`
- :ref:`using-oci-image`
- :ref:`using-freebsd`

If you are interested in contributing to mqttwarn, you should setup a development
sandbox, see :ref:`sandbox`.

Configuration file
==================

Before running mqttwarn, you will need a configuration file.

The path to the configuration file is obtained from the ``MQTTWARNINI`` environment
variable, and defaults to ``mqttwarn.ini`` in the current directory.
On server installations, the default configuration file is located at
``/etc/mqttwarn/mqttwarn.ini``.

You can create a configuration file blueprint easily::

   mqttwarn make-config


Running
=======

In order to start the program, just type::

   mqttwarn

or::

   MQTTWARNINI=/path/to/mqttwarn.ini mqttwarn



.. toctree::
   :hidden:

   pip
   oci
   freebsd
   standalone
