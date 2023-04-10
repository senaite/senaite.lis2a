Push Consumer
-------------

The ASTM-like messages are received by `senaite.lis2a`_ through a
`JSONAPI's "push" custom endpoint`_. `senaite.serial.cli`_ sends the data read
from serial devices to this endpoint each time a transfer phase is completed.

Running this test from the buildout directory:

    bin/test test_textual_doctests -m senaite.lis2a -t PushConsumer

Test Setup
~~~~~~~~~~

Needed imports:

    >>> import itertools
    >>> import json
    >>> import transaction
    >>> import urllib
    >>> from bika.lims import api as _api
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.lis2a import api
    >>> from senaite.jsonapi.interfaces import IPushConsumer
    >>> from senaite.lis2a.interpreter import Interpreter
    >>> from senaite.lis2a.tests import utils
    >>> from zope.component import queryAdapter

Variables:

    >>> portal = self.portal
    >>> portal_url = portal.absolute_url()
    >>> api_url = "{}/@@API/senaite/v1".format(portal_url)
    >>> browser = self.getBrowser()
    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])
    >>> transaction.commit()

Functional Helpers:

    >>> def post(url, data):
    ...     url = "{}/{}".format(api_url, url)
    ...     browser.post(url, urllib.urlencode(data, doseq=True))
    ...     return browser.contents

Create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])
    >>> utils.setup_baseline_data(portal)
    >>> transaction.commit()


Ensure adapter is available
~~~~~~~~~~~~~~~~~~~~~~~~~~~
    >>> messages = [
    ...     utils.read_file("example_lis2a2_01.txt"),
    ...     utils.read_file("example_lis2a2_02.txt"),
    ... ]
    >>> payload = {
    ...     "consumer": "senaite.lis2a.import",
    ...     "messages": messages,
    ... }
    >>> consumer = queryAdapter(payload, IPushConsumer, name="senaite.lis2a.import")
    >>> consumer is not None
    True

Send messages via push
~~~~~~~~~~~~~~~~~~~~~~~

Now, try to send messages with valid sample ids and keywords. Create two
samples and receive them first:

    >>> samples = map(lambda a: utils.create_sample(), range(2))
    >>> success = map(lambda s: do_action_for(s, "receive"), samples)
    >>> transaction.commit()

Make the messages match with the sample ids:

    >>> sample_ids = map(_api.get_id, samples)
    >>> base_message = utils.read_file("example_lis2a2_01.txt")
    >>> base_message = base_message.replace("^A1", "^Cu")
    >>> base_message = base_message.replace("^A2", "^Fe")
    >>> messages = map(lambda s: base_message.replace("927529", s), sample_ids)

Send the messages:

    >>> payload.update({"messages": messages})
    >>> post("push", payload)
    '..."success": true...'

Confirm that results have been submitted:

    >>> transaction.commit()
    >>> analyses = map(lambda s: s.getAnalyses(full_objects=True), samples)
    >>> analyses = list(itertools.chain.from_iterable(analyses))
    >>> all(map(lambda a: a.getResult(), analyses))
    True

    >>> list(set(map(_api.get_review_status, analyses)))
    ['to_be_verified']

And both samples are now in "to_be_verified" status:

    >>> map(_api.get_review_status, samples)
    ['to_be_verified', 'to_be_verified']


.. Links

.. _senaite.lis2a: https://pypi.python.org/pypi/senaite.lis2a
.. _JSONAPI's "push" custom endpoint: https://senaitejsonapi.readthedocs.io/en/latest/extend.html#push-endpoint-custom-jobs
.. _senaite.serial.cli: https://pypi.python.org/pypi/senaite.serial.cli

