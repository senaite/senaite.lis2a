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
            from senaite.lis2a.api import get_builtin_interpreters
            base_configuration = get_builtin_interpreters()[0]
            if not base_configuration:
                raise ValueError("No interpreter found for {}".format(extends))

        # Make a deep copy to not mess things around
        kw = copy.deepcopy(base_configuration)
        conf = copy.deepcopy(configuration)
        for key in "HPORCQLSM":
            values = kw.pop(key, {})
            values.update(conf.pop(key, {}))
            kw[key] = values
        kw.update(conf)
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

    def get_message_values(self, key):
        """Returns the values for the key passed-in from the whole message
        :param key: <record_type>.<field_name> (O.SpecimenID, H.SenderName,..)
        :return: a list of values that match with the key passed in.
        """
        # Get the key of the record to look at
        record_type = self.get_record_type(key)

        # Get the records for this record type
        records = msgapi.get_records(self.message, record_type)
        if not records:
            return []

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
        """Returns whether the current interpreter supports the message, based
        on the "selection_criteria" setting.

        If the selection criteria for current interpreter contains a list, the
        function returns True only if all criteria are met.

        Likewise, if a selection criteria maps to more than one record from the
        message, the target value from all records must match with the criteria.

        If the expected value of a selection criteria is a list, the message
        value must match with at least one of the items of the list (OR).

        :param message: message to evaluate against the selection criteria
        :return: true if current interpreter supports the message provided
        """
        if not self.selection_criteria:
            raise ValueError("No selection criteria set")

        if not msgapi.is_compliant(message):
            return False

        if msgapi.is_composite(message):
            # This interpreter cannot handle multi-(O)rder messages
            # In accordance with LIS2-A2, the SampleID/SpecimenID is stored in
            # (O)rder record (SpecimenID and InstrumentSpecimenID fields) and
            # we expect all (R)esult records from this message to belong to the
            # same specimen
            return False

        # Read the message with current interpreter
        self.read(message)

        # The interpreter can handle the message only if all criteria are met
        supported = False
        for key, expected_value in self.selection_criteria.items():

            # Get the message values for the key (<record_type>.<field_name>)
            values = self.get_message_values(key)

            # All values must match with the expected value. If the expected
            # value is a list, the value must match with at least one of the
            # expected values
            matches = map(lambda v: self.match(v, expected_value), values)
            supported = matches and all(matches)
            if not supported:
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
        if value is None:
            value = ""
        if expected_value is None:
            expected_value = ""
        if isinstance(expected_value, six.string_types):
            expected_value = [expected_value.strip(), ]
        return value.strip() in expected_value

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

    def get_mapped_values(self, mapping_id, record):
        """Return a list with the mapped values for the mapping id passed in
        """
        key = self.get_mapped_keys(mapping_id)
        if self.is_field_key(key):
            value = [self.get_record_value(key, record)]
        else:
            value = map(lambda k: self.get_record_value(k, record), key)
        return filter(None, value)

    def get_result_value(self, record):
        """Returns the mapped result value from the record in accordance with
        the configuration set for this interpreter
        """
        values = self.get_mapped_values("result", record)
        if values:
            # TODO Return the first one
            return values[0]
        return None

    def get_analysis_keywords(self, record):
        """Returns the mapped analysis keyword(s) from the record in accordance
        with the configuration set for this interpreter
        """
        return self.get_mapped_values("keyword", record)

    def get_capture_date(self, record):
        """Returns the mapped capture date from the record, in accordance with
        the configuration set for this interpreter
        """
        # Sort them (ANSI X3.30.2 format) and return the last one
        capture_dates = self.get_mapped_values("capture_date", record)
        capture_dates.sort()
        return capture_dates and capture_dates[-1] or None

    def get_sample_ids(self):
        """Returns the mapped sample ids from the message, in accordance with
        the configuration set for this interpreter
        """
        sample_id_keys = self.get_mapped_keys("id")

        # Return the sample ids found for the mapped keys
        sample_ids = map(self.get_message_values, sample_id_keys)
        return list(itertools.chain.from_iterable(sample_ids))

    def is_field_key(self, thing):
        """Returns whether the thing is a field key or not
        """
        try:
            self.split_key(thing)
            return True
        except ValueError:
            pass
        return False

    def to_result_data(self, result_record, interim_records):
        """Returns a dict representing the result data information
        """
        # Get the potential sample ids from this message
        # Current message is for one specimen/sample only, but different ids
        # for finding matches in SENAITE might be provided (worksheet id,
        # sample id, client sample id, etc.)
        sample_ids = self.get_sample_ids()

        def resolve_result_mappings(record):
            capture_date = self.get_capture_date(record)
            capture_date = self.to_date(capture_date, default=datetime.now())
            return {
                "id": sample_ids,
                "keyword": self.get_analysis_keywords(record),
                "result": self.get_result_value(record),
                "capture_date": capture_date,
            }

        def resolve_interim_mappings(interim_record):
            interim_fields = []
            result = self.get_result_value(interim_record)
            keywords = self.get_analysis_keywords(interim_record)
            for keyword in keywords:
                interim_fields.append({keyword: result})
            return interim_fields

        # Resolve mappings for result
        data = resolve_result_mappings(result_record)

        # id and keyword are required
        if not all([data["id"], data["keyword"]]):
            return {}

        # Resolve mappings for interim fields
        interim_data = {}
        interim_list = map(resolve_interim_mappings, interim_records)
        interim_list = list(itertools.chain.from_iterable(interim_list))

        # Convert the list of interim dicts to a single dict
        for interim in interim_list:
            interim_data.update(interim)

        # Update the results record with interims
        data.update({"interims": interim_data})

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
            # Include the rest of result records as interim fields
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
