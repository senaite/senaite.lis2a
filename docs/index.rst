senaite.lis2a
=============

This add-on enables the import of data compliant with the industry supported
standard CLSI (`Clinical and Laboratory Standards Institute`_, formerly NCCLS)
`LIS2-A2`_ *"Specification for Transferring Information Between Clinical
Laboratory Instruments and Information Systems"*, a revision of `ASTM E1394-97`_.

`senaite.lis2a`_ makes use of `senaite.jsonapi`_ by registering an `IPushConsumer`
adapter, in charge of the interpretation of LIS2-A2 incoming data.

This package is not for the transmission or data exchange across RS-232 or TCP/IP,
but provides an HTTP route to *push* results data that are compliant with
LIS2-A2. For serial binary data exchange compliant with `LIS1-A`_, please look at
the command line tool `senaite.serial.cli`_.

For high-demand instances, is strongly recommended to use this add-on together
with `senaite.queue`_. senaite.lis2a delegates the import of results to
senaite.queue when installed and active. Otherwise, the import of results takes
place in a single transaction as soon as the data is received.

.. note:: In 2001, `ASTM Committee E31`_ decided to restructure its operations,
   with the intent of focusing on standards-development issues such as security,
   privacy, and the electronic health record. Part of the reorganization plan
   was to transfer responsibility for E31.13 standards to NCCLS. Following this
   transfer, standard ASTM E1394 was redesignated as NCCLS standards LIS2-A2.

Table of Contents:

.. toctree::
   :maxdepth: 2

   installation
   changelog


.. Links

.. _SENAITE LIMS: https://www.senaite.com
.. _senaite.lis2a: https://pypi.python.org/pypi/senaite.lis2a
.. _Clinical and Laboratory Standards Institute: https://clsi.org
.. _LIS1-A: https://clsi.org/standards/products/automation-and-informatics/documents/lis01/
.. _LIS2-A2: https://clsi.org/standards/products/automation-and-informatics/documents/lis02/
.. _senaite.jsonapi: https://pypi.python.org/pypi/senaite.jsonapi
.. _senaite.serial.cli: https://pypi.python.org/pypi/senaite.lis2a
.. _senaite.queue: https://pypi.python.org/pypi/senaite.queue
.. _ASTM Committee E31: https://www.astm.org/COMMITTEE/E31.htm
.. _ASTM E1394-97: https://www.astm.org/Standards/E1394.htm
