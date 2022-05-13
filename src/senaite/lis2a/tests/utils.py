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

import os

from DateTime import DateTime

from bika.lims import api as _api
from bika.lims.utils.analysisrequest import create_analysisrequest


def get_test_file(file_name):
    resources_path = os.path.abspath(os.path.dirname(__file__))
    resources_path = "{}/resources".format(resources_path)
    return "{}/{}".format(resources_path, file_name)


def read_file(file_name):
    file_path = get_test_file(file_name)
    with open(file_path, "r") as f:
        output = f.readlines()
        return "".join(output)


def setup_baseline_data(portal):
    """Setups baseline data for testing purposes
    """
    setup = portal.bika_setup
    client = _api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    contact = _api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    sample_type = _api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    lab_contact = _api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    department = _api.create(setup.bika_departments, "Department", title="Chemistry", Manager=lab_contact)
    category = _api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    Cu = _api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())
    Fe = _api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Category=category.UID())


def get_service(keyword):
    """Returns the service for the given keyword
    """
    folder = _api.get_setup().bika_analysisservices
    for obj in folder.objectValues():
        if obj.getKeyword() == keyword:
            return obj
    return None


def get_objects(portal_type, **kwargs):
    """Returns all objects from the given type
    """
    query = kwargs and kwargs or {}
    query.update({"portal_type": portal_type})
    catalog_id = "uid_catalog"
    if "catalog" in query:
        catalog_id = query.pop("catalog")
    return map(_api.get_object, _api.search(query, catalog_id))


def get_object(portal_type, **kwargs):
    objs = get_objects(portal_type, **kwargs)
    return objs and objs[0] or None


def create_sample(keywords=None, **kwargs):
    """Creates a new sample
    """
    values = kwargs and kwargs or {}
    request = _api.get_request()
    date_sampled = DateTime().strftime("%Y-%m-%d")
    values.update({
        "DateSampled": values.get("DateSampled") or date_sampled,
    })
    to_update = ["Client", "Contact", "SampleType"]
    for portal_type in to_update:
        field_value = values.get(portal_type)
        if not field_value:
            field_value = _api.get_uid(get_object(portal_type))
            values[portal_type] = field_value

    services = None
    if "services" in values:
        services = values.pop("services")

    if not services:
        services = get_objects("AnalysisService")

    services = map(_api.get_uid, services)
    client = _api.get_object_by_uid(values.get("Client"))
    sample = create_analysisrequest(client, request, values, services)
    return sample


def filter_by_state(brains_or_objects, state):
    """Filters the objects passed in by state
    """
    objs = map(_api.get_object, brains_or_objects)
    return filter(lambda obj: _api.get_review_status(obj) == state, objs)
