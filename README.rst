CLIS LIS2-A results import for SENAITE
======================================

.. image:: https://img.shields.io/pypi/v/senaite.lis2a.svg?style=flat-square
    :target: https://pypi.python.org/pypi/senaite.lis2a

.. image:: https://img.shields.io/travis/senaite/senaite.lis2a/master.svg?style=flat-square
    :target: https://travis-ci.org/senaite/senaite.lis2a

.. image:: https://readthedocs.org/projects/pip/badge/
    :target: https://senaitelis2a.readthedocs.org

.. image:: https://img.shields.io/github/issues-pr/senaite/senaite.lis2a.svg?style=flat-square
    :target: https://github.com/senaite/senaite.lis2a/pulls

.. image:: https://img.shields.io/github/issues/senaite/senaite.lis2a.svg?style=flat-square
    :target: https://github.com/senaite/senaite.lis2a/issues

.. image:: https://img.shields.io/badge/Made%20for%20SENAITE-%E2%AC%A1-lightgrey.svg
   :target: https://www.senaite.com


About
-----

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


Documentation
-------------

* https://senaitelis2a.readthedocs.io

Feedback and support
--------------------

* `Community site`_
* `Gitter channel`_
* `Users list`_

License
-------

**SENAITE.LIS2A** Copyright (C) 2020 RIDING BYTES & NARALABS

This program is free software; you can redistribute it and/or modify it under
the terms of the `GNU General Public License version 2`_ as published by the
Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.


.. Links

.. _SENAITE LIMS: https://www.senaite.com
.. _senaite.lis2a: https://pypi.python.org/pypi/senaite.lis2a
.. _Clinical and Laboratory Standards Institute: https://clsi.org
.. _LIS1-A: https://clsi.org/standards/products/automation-and-informatics/documents/lis01/
.. _LIS2-A2: https://clsi.org/standards/products/automation-and-informatics/documents/lis02/
.. _senaite.jsonapi: https://pypi.python.org/pypi/senaite.jsonapi
.. _senaite.serial.cli: https://pypi.python.org/pypi/senaite.lis2a
.. _senaite.queue: https://pypi.python.org/pypi/senaite.queue
.. _ASTM E1394-97: https://www.astm.org/Standards/E1394.htm
.. _Community site: https://community.senaite.org/
.. _Gitter channel: https://gitter.im/senaite/Lobby
.. _Users list: https://sourceforge.net/projects/senaite/lists/senaite-users
.. _GNU General Public License version 2: https://github.com/senaite/senaite.lis2a/blob/master/LICENSE
