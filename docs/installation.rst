Installation
============

To install senaite.lis2a in your SENAITE instance, simply add this add-on
in your buildout configuration file as follows, and run `bin/buildout`
afterwards:

.. code-block:: ini

    [buildout]

    ...

    [instance]
    ...
    eggs =
        ...
        senaite.lis2a


With this configuration, buildout will download and install the latest published
release of `senaite.lis2a from Pypi`_.

.. note:: For high-demand instances, is strongly recommended to use this add-on
   together with `senaite.queue`_. senaite.lis2a delegates the import of results
   to senaite.queue when installed and active. Otherwise, the import of results
   takes place in a single transaction as soon as the data is received.


.. Links

.. _senaite.lis2a from Pypi: https://pypi.org/project/senaite.lis2a
.. _senaite.queue: https://pypi.python.org/pypi/senaite.queue