# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIS2A.
#
# SENAITE.LIS2A is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import itertools
import json
from os.path import isfile

import analysis as anapi
import message as msgapi
import six
from pkg_resources import resource_listdir
from senaite.lis2a import PRODUCT_NAME
from senaite.lis2a.interpreter import Interpreter
from senaite.lis2a.interpreter import lis2a2

from bika.lims import api

try:
    # SENAITE.QUEUE might or not might be installed
    from senaite.queue import api as queueapi
    from senaite.queue import is_installed as is_queue_installed
except Exception:
    queue = None
    is_queue_installed = None

# ID of the results import task for the queue
QUEUE_TASK_ID = "task_senaite_lis2a_import"


_marker = object()


def is_queue_available():
    """Returns whether senaite.queue add-on is available and enabled
    """
    available = False
    if all([queueapi, is_queue_installed]):
        available = is_queue_installed() and queueapi.is_queue_enabled()
    return available


def queue_import(messages):
    """Add the LIS2-A compliant message(s) to the import results queue
    :param messages: str message or a list of messages
    """
    if not is_queue_available():
        raise RuntimeError("Cannot queue message. SENAITE.QUEUE not available")

    if not messages:
        return False

    if isinstance(messages, six.string_types):
        messages = (messages, )

    context = api.get_setup().bika_instruments
    params = {
        "messages": messages,
        "priority": 50,
        "ghost": True,
    }
    return queueapi.add_task(QUEUE_TASK_ID, context, **params)


def import_message(message, interpreter=None):
    """Imports the result from the LIS2-A compliant message passed-in
    :param message: str representing a full LIS2-A compliant message
    """
    # Get the results data dicts
    data = extract_results(message, interpreter=interpreter)

    # Try to import the results. At least one result should be imported
    return any(map(anapi.import_result, data))


def extract_results(message, interpreter=None):
    """Returns a list of result data dicts. A given message can contain multiple
    records from (R)esult type, so it returns a list of dicts, and each dict
    represents a potential results for a single test
    """
    # The message might be composite. This is, a single message can contain
    # results for more than one sample
    if msgapi.is_composite(message):
        messages = msgapi.split_message(message)
        results = map(lambda m: extract_results(m, interpreter), messages)
        return any(list(itertools.chain.from_iterable(results)))

    if not interpreter:
        # Look for a suitable interpreter
        interpreter = get_interpreter_for(message)
        if not interpreter:
            raise ValueError("No interpreter found for {}".format(message))

    interpreter.read(message)
    results_data = interpreter.get_results_data()
    interpreter.close()
    return results_data


def get_interpreter_for(message, default=None):
    """Returns the interpreter that can be used for the interpretation of the
    message passed-in, if any
    """
    # The message might be composite
    if msgapi.is_composite(message):
        messages = msgapi.split_message(message)
        interpreters = map(get_interpreter_for, messages)
        ids = map(lambda i: i and i.id or None, interpreters)
        if len(list(set(ids))) == 1:
            return interpreters[0]
        return default

    for interpreter in get_interpreters():
        if interpreter.supports(message):
            return interpreter
    return default


def get_interpreters():
    """Returns the result import definitions available in the system
    """
    # Get JSON configuration files from resources dir
    files = resource_listdir(PRODUCT_NAME, "resources")
    files = filter(lambda file_name: file_name.endswith(".json"), files)

    # Get the interpreters
    interpreters = map(get_interpreter_from_json, files)

    # Extend with built-in interpreters
    builtin = get_builtin_interpreters()
    interpreters.extend(builtin)

    return interpreters


def get_interpreter(id):
    """Returns an interpreter by id
    """
    interpreters = get_interpreters()
    interpreter = filter(lambda i: i.id == id, interpreters)
    if len(interpreter) > 1:
        raise ValueError("More than one interpreter found for '{}'".format(id))
    return interpreter and interpreter[0] or None


def get_builtin_interpreters():
    """Returns the built-in interpreters that are compliant with standards
    """
    configs = [lis2a2.CONFIGURATION, ]
    return map(Interpreter, configs)


def get_interpreter_from_json(str_or_file):
    """Returns an interpreter built from a json resource
    """
    if isfile(str_or_file):
        with open(str_or_file, "r") as f:
            str_or_file = f.read()
    return Interpreter(json.loads(str_or_file))
