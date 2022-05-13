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

import re


def is_compliant(message):
    """A message should have at least a header record
    """
    try:
        header = get_header(message)
        if header:
            return True
    except ValueError:
        pass
    return False


def is_composite(message):
    """Returns whether the message is made of multiple messages
    """
    msgs = split_message(message)
    return len(msgs) > 1


def get_header(message):
    """Returns the header record of the LIS-2A compliant message
    """
    # The header shall contain identifiers of both the sender and the receiver.
    # The message header is a level zero record and must be followed at some
    # point by a message terminator record before ending the session or
    # transmitting another header record. This record type must always be the
    # first record in a transmission.
    # H<field_delimiter><repeat_delimiter><component_delimiter><escape_delimiter>
    records = get_raw_records(message)
    header = records and records[0] or ""
    if is_header_record(header):
        return header

    raise ValueError("Message not compliant with LIS2-A. No valid header (H)")


def is_header_record(record):
    """Returns whether the record passed-in is a (H)eader record
    """
    # The five Latin-1 characters that immediately follow the H (the header ID)
    # define the delimiters to be used throughout the subsequent records of the
    # message. The second character in the header record is the field delimiter,
    # the third character is the repeat delimiter, the fourth character is the
    # component delimiter, and the fifth is the escape character. A field
    # delimiter follows these chars to separate them from subsequent fields.
    # Using the example delimiters, the first six characters in the header
    # record would appear as follows: H|\ˆ&|.
    if re.match(r'^H\W{5}', record):
        if record[1] == record[5]:
            # Be sure delimiters are not repeated
            if len(set(record[1:5])) == 4:
                return True
    return False


def get_field_delimiter(message):
    """Returns the field delimiter
    """
    return get_header(message)[1]


def get_repeat_delimiter(message):
    """Returns the repeat delimiter
    """
    return get_header(message)[2]


def get_component_delimiter(message):
    """Returns the repeat delimiter
    """
    return get_header(message)[3]


def get_escape_delimiter(message):
    """Returns the escape delimiter
    """
    return get_header(message)[4]


def get_records(message, record_type):
    """Returns the list of records for the record type
    """
    field_delimiter = get_field_delimiter(message)

    def is_match(record):
        return record[0:2] == "{}{}".format(record_type, field_delimiter)

    return filter(is_match, get_raw_records(message))


def get_record(message, record_type):
    """Returns the first record for the record type passed in
    """
    records = get_records(message, record_type)
    record = records and records[0] or None
    return record


def get_raw_records(message):
    """Returns a list with the records of the LIS2-A message
    """
    lines = map(lambda l: l.strip(), message.split("\n"))
    return filter(None, lines)


def get_value_at(record, position, field_delimiter="|",
                 component_delimiter="^"):
    """Returns the value from the message record at the given position
    :param record: message record
    :param position: tuple of (field_index, component_index) or int
    :param field_delimiter: delimiter for fields
    :param component_delimiter: delimiter for field components
    """
    if isinstance(position, int):
        position = (position, 0)

    # TODO e.g. See SpecimenID
    # Split the record by field delimiter
    field = record.split(field_delimiter)
    if len(field) <= position[0]:
        raise ValueError("Missing field at position {}".format(position[0]))
    field = field[position[0]]

    # Split the field by component delimiter
    components = field.split(component_delimiter)
    if len(components) <= position[1]:
        raise ValueError("Missing component at position {}".format(position))

    return components[position[1]]


def split_message(message):
    """Split the message into a list of messages, each one containing a battery
    of results for same Specimen. Common records are preserved in every single
    message generated.
    """
    messages = []
    curr_msg = []

    # Keep reading through the records of this message
    for record in get_raw_records(message):
        if not record:
            continue

        # Get the last record we've added in our previous iteration
        last_record = curr_msg and curr_msg[-1] or None
        if not last_record:
            # Current record must be a header
            if is_header_record(record):
                curr_msg.append(record)
            continue

        record_type = record[0]
        record_types = map(lambda m: m[0], curr_msg)
        if record_type not in record_types:
            # This is child node
            curr_msg.append(record)

        elif record_type == "R":
            # This is a leaf, keep adding
            curr_msg.append(record)

        else:
            # This is a parent node
            str_msg = "\n".join(curr_msg)
            messages.append(str_msg)

            # Go up in the hierarchy
            idx = record_types.index(record_type)
            curr_msg = curr_msg[:idx]
            curr_msg.append(record)

    if curr_msg:
        str_msg = "\n".join(curr_msg)
        messages.append(str_msg)

    return filter(is_compliant, messages)
