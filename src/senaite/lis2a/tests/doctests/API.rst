LIS2A API
---------

`senaite.lis2a` comes with an api to facilitate the usage of the package.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t API

Test Setup
~~~~~~~~~~

Needed imports:

    >>> import json
    >>> import os
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.lis2a import api
    >>> from senaite.lis2a.interpreter import Interpreter

Variables:

    >>> portal = self.portal
    >>> resources_path = os.path.abspath(os.path.dirname(__file__))
    >>> resources_path = "{}/../resources".format(resources_path)

Some helpers:

    >>> def read_file(file_name):
    ...     file_path = "{}/{}".format(resources_path, file_name)
    ...     with open(file_path, "r") as f:
    ...         output = f.readlines()
    ...     return "".join(output)

Create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

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

    >>> json_config = '{"id": "custom_interpreter", "extends": "LIS2-A2", "selection_criteria": {"H.SenderName": "my own device"}}'
    >>> custom_interpreter = api.get_interpreter_from_json(json_config)
    >>> custom_interpreter.id
    u'custom_interpreter'

From a .json file too:

    >>> json_file = "{}/abbottm2000.json".format(resources_path)
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

    >>> message = read_file("example_lis2a2_01.txt")
    >>> interpreter = api.get_interpreter_for(message)
    >>> isinstance(interpreter, Interpreter)
    True

    >>> interpreter.id
    'LIS2-A2'

Even if the message is composite:

    >>> message = read_file("example_lis2a2_02.txt")
    >>> interpreter.id
    'LIS2-A2'

But returns None if the message is not supported:

    >>> message = read_file("example_non-lis2a2_01.txt")
    >>> api.get_interpreter_for(message) is None
    True


Extracting results from a message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can directly extract the results from a message:

    >>> message = read_file("example_lis2a2_01.txt")
    >>> api.extract_results(message)

