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

from DateTime import DateTime
from senaite.lis2a import logger

from bika.lims import api
from bika.lims import LDL
from bika.lims import UDL
from bika.lims import workflow as wf
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IWorksheet

_marker = object()


def import_result(data):
    """Tries to import the result data passed in
    :param data: dict representation of a result, suitable for import

    data = {
        "id": <str/list with the ID/s (SampleID, SampleClientID,Worksheet ID)>,
        "keyword": <str/list with analysis keyword>,
        "result": <analysis result>,
        "capture_date": <DateTime when the result was captured>,
        "interims": {
            <interim_keyword>: <interim_result>,
            ...
        ],
        ...
    }

    "id" and "keyword" are used to find analyses that match with any of the
    ids passed-in, together with any of the keywords passed-in.
    """
    ids = data.get("id")
    ids = list(set(ids))
    keywords = data.get("keyword")
    if not all([ids, keywords]):
        logger.error("id or keyword are missing or empty")
        return False

    # Look for matches
    analysis = search_analysis(ids, keywords)
    if not analysis:
        logger.error("no match found for ids {} and keywords {}"
                     .format(repr(ids), repr(keywords)))
        return False

    # Get the original result for later comparison
    original_result = analysis.getResult()

    if data.get("remove_interims"):
        # Purge interim fields
        analysis.setInterimFields([])

    else:
        # Purge non-existent interim fields and fill others
        interim_fields = get_interims_for(analysis, data)
        if interim_fields:
            analysis.setInterimFields(interim_fields)
            analysis.calculateResult(override=True)

    # store results ranges if necessary
    ranges = data.get("ranges", None)
    ranges = to_results_range(ranges, default=None)
    if ranges:
        ranges.update({
            "uid": api.get_uid(analysis),
            "keyword": analysis.getKeyword(),
        })
        analysis.setResultsRange(ranges)

    # If no result has been calculated, set the result directly
    result = stringify(data["result"])
    if result and analysis.getResult() == original_result:

        # Maybe the result is a Detection Limit
        if is_detection_limit(result):
            # We do want to store the detection limit, even if the manual
            # detection limit for the analysis is set to False
            analysis.setAllowManualDetectionLimit(True)
            analysis.setDetectionLimitOperand(result[0])
            result = result[1:].strip()

        # Set the final result
        analysis.setResult(result)

    # If the final result changed, then set the capture date that comes
    # from the device and submit
    if analysis.getResult() != original_result:
        capture_date = data.get("capture_date", DateTime())
        analysis.setResultCaptureDate(capture_date)

        # Submit the result
        wf.doActionFor(analysis, "submit")

    return True


def to_results_range(value, default=_marker):
    """Converts the value to a valid results range dict
    """
    if not isinstance(value, six.string_types):
        if default is _marker:
            raise TypeError("Not supported type")
        return default

    # e.g. [.58 - 1.59]
    values = [val.strip() for val in value.split("-")]
    values = filter(None, values)
    if len(values) != 2:
        if default is _marker:
            raise ValueError("Not a valid result range: {}".format(value))
        return default

    min_value = values[0][1:]
    if not api.is_floatable(min_value):
        if default is _marker:
            raise ValueError("Not a valid result range: {}".format(value))
        return default

    max_value = values[1][:-1]
    if not api.is_floatable(max_value):
        if default is _marker:
            raise ValueError("Not a valid result range: {}".format(value))
        return default

    min_operators = {"[": "qeq", "(": "gt"}
    min_operator = min_operators.get(values[0][:1])
    if not min_operator:
        if default is _marker:
            raise ValueError("Not a valid result range: {}".format(value))
        return default

    max_operators = {"]": "leq", ")": "lt"}
    max_operator = max_operators.get(values[1][-1:])
    if not max_operator:
        if default is _marker:
            raise ValueError("Not a valid result range: {}".format(value))
        return default

    min_value = api.to_float(min_value)
    max_value = api.to_float(max_value)
    if min_value > max_value:
        if default is _marker:
            raise ValueError("Not a valid result range: {}".format(value))
        return default

    return {
        "min": min_value,
        "max": max_value,
        "min_operator": min_operator,
        "max_operator": max_operator,
    }


def is_detection_limit(result):
    """Returns whether the result is actually a Detection Limit
    """
    if len(result) > 1:
        return result[0] in [LDL, UDL]
    return False


def search_analysis(container_ids, analysis_keywords):
    """Search an analysis for the given container id and keyword.
    :param container_id: Sample ID, Worksheet ID, Client SampleID, RefSampleID
    :param analysis_keyword: Analysis keyword
    """
    # Search for the analysis container (Sample or Worksheet)
    container = search_analysis_container(container_ids)
    if not container:
        return None

    # Search analysis with the given keyword from the container
    analysis = search_analysis_from(container, analysis_keywords)
    if not analysis:
        # Try with reference analysis (Blanks, Controls and Duplicates)
        analysis = search_reference_analysis(container_ids, analysis_keywords)

    return analysis


def search_reference_analysis(reference_ids, analysis_keywords):
    """Search a reference analysis (Control, Blank or Duplicate) for the
    given reference id and keyword
    """
    query = dict(portal_type=["ReferenceAnalysis", "DuplicateAnalysis"],
                 getReferenceAnalysesGroupID=reference_ids,
                 getKeyword=analysis_keywords,
                 review_state=["unassigned", "assigned"])
    analyses = api.search(query, CATALOG_ANALYSIS_LISTING)

    # Look for unique result
    if len(analyses) == 1:
        return api.get_object(analyses[0])

    return None


def search_analysis_from(container, keywords):
    """Searches an analysis with the specified keyword within the container
    """
    # Base query
    query = dict(
        getKeyword=keywords,
        portal_type="Analysis",
        review_state=["unassigned", "assigned"]
    )

    # Build the query
    container = api.get_object(container)
    container_uid = api.get_uid(container)
    if IAnalysisRequest.providedBy(container):
        query.update({"getAncestorsUIDs": container_uid})

    elif IWorksheet.providedBy(container):
        query.update({"getWorksheetUID": container_uid})

    else:
        path = api.get_path(container)
        raise ValueError("Could not get analyses from {}".format(path))

    # Search for a unique result
    analyses = api.search(query, CATALOG_ANALYSIS_LISTING)
    if len(analyses) == 1:
        return api.get_object(analyses[0])

    return None


def search_analysis_container(container_ids):
    """Searches an analysis container (Sample or Worksheet) for the id. The
     priority for searches is as follows: Sample ID, Worksheet ID, Client
     Sample ID
    """
    # Try by Sample ID (only received samples can be submitted)
    query = dict(portal_type="AnalysisRequest", getId=container_ids,
                 review_state="sample_received")
    sample = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    if sample:
        return api.get_object(sample[0])

    # Try by Worksheet ID (only open worksheets)
    query = dict(portal_type="Worksheet", review_state="open",
                 getId=container_ids)
    worksheet = api.search(query, CATALOG_WORKSHEET_LISTING)
    if worksheet:
        return api.get_object(worksheet[0])

    # Try by Client Sample ID
    query = dict(portal_type="AnalysisRequest", getClientSampleID=container_ids,
                 review_state="sample_received")
    sample = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    if sample:
        return api.get_object(sample[0])

    return None


def get_interims_for(analysis, result_data):
    """Returns the interims to be applied to the analysis specified based
    on the data item provided
    """
    data_interims = result_data.get("interims")
    if not data_interims:
        return False

    interims = list(analysis.getInterimFields() or [])
    if not interims:
        return False

    for index in range(len(interims)):
        keyword = interims[index]["keyword"]
        title = interims[index]["title"]

        # Try to get the value for this interim field from data_item
        value = stringify(data_interims.get(keyword, None))
        if not value:
            # Try with the title
            value = stringify(data_interims.get(title, None))
            if not value:
                continue

        # Set the interim field value
        interims[index]["value"] = value

    return interims


def stringify(value):
    """Return the value stringified, with None becoming empty string
    """
    if value is None:
        return ""
    return str(value).strip()
