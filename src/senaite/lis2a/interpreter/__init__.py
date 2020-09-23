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

import copy
import itertools
from datetime import datetime

import lis2a2
import six
from senaite.lis2a.api import message as msgapi

_marker = object()


class Interpreter(dict):

    def __init__(self, configuration):
        """Creates a new instance of interpreter with the definition provided
        """
        base_configuration = {}
        extends = configuration.get("extends")
        if extends:
            # This configuration extends from another
            from senaite.lis2a.api import get_interpreter
            base_configuration = get_interpreter(extends)
            if not base_configuration:
                raise ValueError("No interpreter found for {}".format(extends))

        # Make a deep copy to not mess things around
        kw = copy.deepcopy(base_configuration)
        kw.update(configuration)
        super(Interpreter, self).__init__(**kw)

        self.message = None
        self.field_delimiter = None
        self.component_delimiter = None
        self.repeat_delimiter = None
        self.escape_delimiter = None

    @property
    def id(self):
        return self["id"]

    @property
    def selection_criteria(self):
        return self.get("selection_criteria", {})

    @property
    def result_criteria(self):
        return self.get("result_criteria", {})

    @property
    def mappings(self):
        return self.get("mappings", {})

    def split_key(self, key):
        """Returns a tuple of 2 items: (record_type, field_name)
        """
        if not isinstance(key, six.string_types):
            raise ValueError("Field key must be a str")

        tokens = key.split(".")
        if len(tokens) != 2:
            raise ValueError("No valid field key: {}".format(key))
        return tuple(tokens)

    def get_record_type(self, key):
        """Returns the record type from key passed-in
        """
        return self.split_key(key)[0]

    def get_position(self, key):
        """Returns the field and component position from the message
        """
        record_type, field_name = self.split_key(key)
        position = self.get(record_type, {}).get(field_name)
        if not position:
            raise ValueError("No position set for key {}".format(key))
        return position

    def get_message_value(self, key, first_only=True):
        """Returns the value for the key passed-in from the whole message. If
        multiple records for the key passed-in, the value from the first record
        found is returned
        """
        # Get the key of the record to look at
        record_type = self.get_record_type(key)

        # Get the first record for this record_type
        records = msgapi.get_records(self.message, record_type)
        if not records:
            return None

        # Do not look in all records, only the first
        if first_only:
            return self.get_record_value(key, records[0])

        # Return the real value from the records
        values = map(lambda r: self.get_record_value(key, r), records)
        return filter(None, values)

    def get_record_value(self, key, record):
        """Returns the value for the key passed-in from the record, if any
        """
        delimiters = {
            "field_delimiter": self.field_delimiter,
            "component_delimiter": self.component_delimiter,
        }
        position = self.get_position(key)
        return msgapi.get_value_at(record, position, **delimiters)

    def supports(self, message):
        """Returns whether the current interpreter can be used for the
        interpretation of the message passed in
        """
        if not self.selection_criteria:
            raise ValueError("No selection criteria set")

        if not msgapi.is_compliant(message):
            return False

        if msgapi.is_composite(message):
            # This interpreter cannot handle multi-(O)rder messages
            return False

        # The definition can handle the message only if all criteria are met
        self.read(message)
        supported = True
        for key, expected_value in self.selection_criteria.items():

            # Get the real value from the message
            value = self.get_message_value(key, message)

            # Compare with the expected value
            if not self.match(value, expected_value):
                supported = False
                break

        self.close()
        return supported

    def read(self, message):
        """Reads the message
        """
        self.message = message
        self.field_delimiter = msgapi.get_field_delimiter(self.message)
        self.component_delimiter = msgapi.get_component_delimiter(self.message)
        self.repeat_delimiter = msgapi.get_repeat_delimiter(self.message)
        self.escape_delimiter = msgapi.get_escape_delimiter(self.message)

    def close(self):
        """Close the interpreter and leaves to the initial status
        """
        self.message = None
        self.field_delimiter = None
        self.component_delimiter = None
        self.repeat_delimiter = None
        self.escape_delimiter = None

    def check_result_criteria(self, record):
        """Returns whether the record passed in matches with the result
        criteria specified by this interpreter
        """
        if not self.result_criteria:
            raise ValueError("No result criteria set")

        # The interpreter can handle the record if all criteria are met
        for key, expected_value in self.result_criteria.items():

            if self.get_record_type(key) != "R":
                raise ValueError("Records other than Result are not supported")

            # Get the real value from the record
            value = self.get_record_value(key, record)

            # Check if value matches with the expected value
            if not self.match(value, expected_value):
                return False

        return True

    def match(self, value, expected_value):
        """Returns whether the value passed in matches with the expected value
        If the expected value is a list, it will return True if the list
        contains the value
        """
        if expected_value is None:
            expected_value = ""
        if isinstance(expected_value, six.string_types):
            expected_value = [expected_value, ]
        return value in expected_value

    def find_result_records(self):
        """Return the result records that match with the result_criteria
        """
        result_records = msgapi.get_records(self.message, "R")
        return filter(self.check_result_criteria, result_records)

    def get_mapped_keys(self, mapping_id):
        """Return the mapped value for the mapping id passed in
        """
        key = self.mappings.get(mapping_id)
        if not key:
            raise ValueError("Mapping '{}' is missing".format(mapping_id))
        return key

    def get_mapped_value(self, mapping_id, record, unique=False):
        """Return the mapped value for the mapping id passed in
        """
        key = self.get_mapped_keys(mapping_id)
        if self.is_field_key(key):
            value = self.get_record_value(key, record)
            if not unique:
                value = filter(None, [value, ])

        elif unique:
            raise ValueError("Mapping '{}' must be unique".format(mapping_id))

        else:
            value = map(lambda k: self.get_record_value(k, record), key)
            value = filter(None, value)

        return value

    def get_result_value(self, record):
        """Returns the mapped result value from the record in accordance with
        the configuration set for this interpreter
        """
        return self.get_mapped_value("result", record, unique=True)

    def get_analysis_keywords(self, record):
        """Returns the mapped analysis keyword(s) from the record in accordance
        with the configuration set for this interpreter
        """
        return self.get_mapped_value("keyword", record)

    def get_capture_date(self, record):
        """Returns the mapped capture date from the record, in accordance with
        the configuration set for this interpreter
        """
        capture_date = self.get_mapped_value("capture_date", record)
        # If more than one found, pick the first one
        if capture_date:
            capture_date = capture_date[0]
        return capture_date and capture_date[0] or None

    def get_sample_ids(self):
        """Returns the mapped sample ids from the message, in accordance with
        the configuration set for this interpreter
        """
        keys = self.get_mapped_keys("id")


        return self.get_message_value("id", first_only=True)

    def is_field_key(self, thing):
        """Returns whether the thing is a field key or not
        """
        try:
            self.split_key(thing)
            return True
        except ValueError:
            return False

    def to_result_data(self, result_record, interim_records):
        """Returns a dict representing the result data information
        """
        # Get the potential sample ids from this message
        import pdb;pdb.set_trace()
        sample_id = self.get_sample_ids()

        def resolve_result_mappings(record):
            capture_date = self.get_capture_date(record)
            capture_date = self.to_date(capture_date, default=datetime.now())
            return {
                "id": sample_id,
                "keyword": self.get_analysis_keywords(record),
                "result": self.get_result_value(record),
                "capture_date": capture_date,
            }

        def resolve_interim_mappings(interim_record):
            interims = []
            result = self.get_result_value(interim_record)
            keywords = self.get_analysis_keywords(interim_record)
            for keyword in keywords:
                interims.append({keyword: result})
            return interims

        # Resolve mappings for result
        data = resolve_result_mappings(result_record)

        # id and keyword are required
        if not all([data["id"], data["keyword"]]):
            return {}

        # Resolve mappings for interims
        interims_data = {}
        interims_list = map(resolve_interim_mappings, interim_records)
        interims_list = list(itertools.chain.from_iterable(interims_list))

        # Convert the list of interim dicts to a single dict
        for interim in interims_list:
            interims_data.update(interim)

        # Update the results record with interims
        data.update({"interims": interims_data})

        # Inject additional options (e.g. remove_interims)
        data.update(self.get("options", {}))
        return data

    def get_results_data(self):
        """Returns a list of dicts containing the result data information to
        store from the message passed-in based on the configuration set for this
        interpreter.
        It is assumed that a given message can contain multiple records from
        (R)esult type, so a list is returned, each result dict representing a
        potential result for a given test. For each result dict, the rest of
        results are also considered under interims field.
        """
        # Extract the result records that match with the result_criteria
        result_records = self.find_result_records()
        if not result_records:
            return {}

        results_data = []
        for record in result_records:
            # Include the rest of result records as interims
            interim_records = filter(lambda r: r != record, result_records)

            # Generate the result data dict
            data = self.to_result_data(record, interim_records)
            if data:
                # Append to the list of results data
                results_data.append(data)

        return results_data

    def to_date(self, ansi_str, default=_marker):
        """
        In all cases, dates shall be recorded in the YYYYMMDD format as required by
        ANSI X3.30.2 December 1, 1989 would be represented as 19891201. When times
        are transmitted, they shall be represented as HHMMSS, and shall be linked
        to dates as specified by ANSI X3.43.3
        Date and time together shall be specified as up to a 14-character
        string: YYYYMMDDHHMMSS
        :param thing:
        :return:
        """
        if isinstance(ansi_str, datetime):
            return ansi_str

        if len(ansi_str) == 8:
            date_format = "%Y%m%d"
        elif len(ansi_str) == 14:
            date_format = "%Y%m%d%H%M%S"
        else:
            if default is _marker:
                raise ValueError("No ANSI format date")
            return default

        try:
            return datetime.strptime(ansi_str, date_format)
        except:
            if default is _marker:
                raise ValueError("No ANSI format date")
            return default
