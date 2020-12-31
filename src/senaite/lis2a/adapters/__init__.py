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

import six
from Products.CMFCore.interfaces import IContentish
from senaite.jsonapi.interfaces import IPushConsumer
from senaite.lis2a import api as _api
from senaite.lis2a.api import message as msgapi
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface

# Maybe senaite.queue is not installed
try:
    from senaite.queue.interfaces import IQueuedTaskAdapter
    from senaite.queue import api as queueapi
    from senaite.queue.queue import get_chunks_for
except:
    IQueuedTaskAdapter = Interface
    queueapi = None


class PushConsumer(object):
    """Adapter that handles push requests for name "senaite.lis2a.import"
    """
    implements(IPushConsumer)

    def __init__(self, data):
        self.data = data

    def process(self):
        """Processes the LIS2-A compliant message. Feeds senaite.queue if
        installed and active. Import the message without delay otherwise

        Each message is a record as defined by Specification E 1394, made of
        multiple frames
        """
        # Extract the full LIS2-A messages from the data
        messages = self.data.get("messages")
        if not messages:
            raise ValueError("No messages found: {}".format(repr(self.data)))

        # Just in case we got a message instead of a list of messages
        if isinstance(messages, six.string_types):
            messages = (messages,)

        # Ensure the messages are LIS2-A compliant
        valid = map(msgapi.is_compliant, messages)
        if not all(valid):
            raise ValueError("Messages are not LIS2-A compliant")

        if _api.is_queue_available():
            # Add the messages to the import results queue. Note we add all
            # messages in a single task, instead of adding a single task for
            # each message. The queue adapter will handle this properly by
            # importing chunks sequentially, making the process more performant
            return _api.queue_import(messages)

        # Try to import the messages immediately
        map(_api.import_message, messages)

        # At this point we always return True, cause "import_results" only
        # returns True if found a match in SENAITE and succeed on the result
        # import. It might happen there is no object in SENAITE matching with
        # the message we are trying to import.
        return True


class QueuedMessageImporter(object):
    """Adapter for the async import of messages
    """
    implements(IQueuedTaskAdapter)
    adapts(IContentish)

    def __init__(self, context):
        self.context = context

    def process(self, task):
        """Process the messages from the task
        """
        messages = task.get("messages", [])
        if queueapi:
            # If there are too many objects to process, split them in chunks to
            # prevent the task to take too much time to complete
            chunks = get_chunks_for(task, items=messages)

            # Process the first chunk
            map(_api.import_message, chunks[0])

            # Add remaining objects to the queue
            _api.queue_import(chunks[1])

        else:
            # Process all them
            map(_api.import_message, messages)
