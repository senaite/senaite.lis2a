LIS2A API
---------

`senaite.lis2a` comes with an api to facilitate the usage of the package.

Running this test from the buildout directory:

    bin/test test_textual_doctests -m senaite.lis2a -t API

Test Setup
~~~~~~~~~~

Needed imports:

    >>> import json
    >>> from bika.lims import api as _api
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.lis2a import api
    >>> from senaite.lis2a.interpreter import Interpreter
    >>> from senaite.lis2a.tests import utils

Variables:

    >>> portal = self.portal

Create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])
    >>> utils.setup_baseline_data(portal)

Retrieve built-in interpreters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

built-in interpreters, compliant with standards are accessible:

    >>> builtin = api.get_builtin_interpreters()
    >>> map(lambda b: b.id, builtin)
    ['LIS2-A2']


Retrieve all interpreters
~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve all available interpreters, built-in included:

    >>> interpreters = api.get_interpreters()
    >>> map(lambda i: i.id, interpreters)
    ['LIS2-A2']


Load an interpreter from JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can load new interpreters from a JSON:

    >>> config = {
    ...     "id": "custom_interpreter",
    ...     "extends": "LIS2-A2",
    ...     "selection_criteria": {
    ...         "H.SenderName": "my own device"
    ...     }
    ... }
    >>> json_config = json.dumps(config)
    >>> custom_interpreter = api.get_interpreter_from_json(json_config)
    >>> custom_interpreter.id
    u'custom_interpreter'

From a .json file too:

    >>> json_file = utils.get_test_file("abbottm2000.json")
    >>> interpreter = api.get_interpreter_from_json(json_file)
    >>> interpreter.id
    u'AbbottM2000'


Loading an interpreter by ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can load an interpreter by it's ID:

    >>> interpreter = api.get_interpreter("LIS2-A2")
    >>> interpreter.id
    'LIS2-A2'

If the interpreter we are looking for does not exist, we get None:

    >>> api.get_interpreter("Dummy") is None
    True


Retrieving a suitable interpreter for a message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given a message, we can ask for a suitable interpreter:

    >>> message = utils.read_file("example_lis2a2_01.txt")
    >>> interpreter = api.get_interpreter_for(message)
    >>> isinstance(interpreter, Interpreter)
    True

    >>> interpreter.id
    'LIS2-A2'

Even if the message is composite:

    >>> message = utils.read_file("example_lis2a2_02.txt")
    >>> interpreter = api.get_interpreter_for(message)
    >>> interpreter.id
    'LIS2-A2'

But returns None if the message is not supported:

    >>> message = utils.read_file("example_non-lis2a2_01.txt")
    >>> api.get_interpreter_for(message) is None
    True


Extracting results from a message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can directly extract the results from a message:

    >>> message = utils.read_file("example_lis2a2_01.txt")
    >>> interpreter = api.get_interpreter_for(message)
    >>> results = api.extract_results(message, interpreter)

And we get one result for each (R)esult record, with the rest of result records
as interim fields:

    >>> len(results)
    2

    >>> map(lambda r: r.get("keyword")[0], results)
    ['A1', 'A2']

    >>> result_1 = results[0]
    >>> result_1.get("id")
    ['927529']

    >>> result_1.get("keyword")
    ['A1']

    >>> result_1.get("result")
    '0.295'

    >>> result_1.get("interims")
    {'A2': '0.312'}

    >>> result_1.get("capture_date")
    datetime.datetime(1989, 3, 27, 13, 22, 47)


Importing a message
~~~~~~~~~~~~~~~~~~~

We can directly import the results from a message:

    >>> message = utils.read_file("example_lis2a2_01.txt")

There is neither a Sample nor Analyses in the system that match, so the
function returns False:

    >>> api.import_message(message)
    False

Let's create and receive a Sample:

    >>> sample = utils.create_sample()
    >>> success = do_action_for(sample, "receive")

Make a message that match with the sample id and service keywords:

    >>> message = """
    ... H|\^&||||||||||P|LIS2-A2|19890327141200
    ... P|1
    ... O|1|{sample_id}||^^^A1\^^^A2
    ... R|1|^^^Cu|0.295||||||||19890327132247
    ... R|2|^^^Fe|0.312||||||||19890327132248
    ... L|1
    ... """
    >>> message = message.strip("\n")
    >>> message = message.replace("{sample_id}", _api.get_id(sample))

On import, the function returns True now:

    >>> api.import_message(message)
    True

Analyses from the sample have a result set:

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> out = dict(map(lambda a: (a.getKeyword(), a.getResult()), analyses))
    >>> out["Cu"]
    '0.295'
    >>> out["Fe"]
    '0.312'

Analyses have been submitted too:

    >>> map(_api.get_review_status, analyses)
    ['to_be_verified', 'to_be_verified']

And the sample is in to be verified as well:

    >>> _api.get_review_status(sample)
    'to_be_verified'

If we try to reimport the same message, nothing happens:

    >>> api.import_message(message)
    False

Extracting query from a message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can directly extract the query from a message:

    >>> message = """
    ... H|\^&||||||||||P|LIS2-A2|19890327141200
    ... Q|1|^2345||ALL^^^|||||||O
    ... L|1|N
    ... """
    >>> interpreter = api.get_interpreter_for(message)
    >>> queries = api.extract_queries(message, interpreter)

And we get one query for the details of a sample:

    >>> len(queries)
    1
    >>> query = queries[0]
    >>> query["id"]
    '1'
    >>> '2345' in query["specimen_id"]
    True
    >>> 'ALL' in query["keyword"]
    True
