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


from senaite.lis2a import logger
from analysis import search_analysis_container

_marker = object()


def process_query(data):
    """Tries to process an query
    :param data: dict representation of a query, suitable for excecution

    data = [{
        'specimen_id': 'AP-0001',
        'id': '1',
        'keyword': ['ALL'],
        'patient_id': 'HH-23-P000001'
    }]

    "specimen_id" is used to identify to the sample/analysis_request
    """
    for query in data:
        specimen_id = query.get("specimen_id")
        keyword = query.get("keyword")
        if not all([keyword, specimen_id]):
            logger.error("specifmen_id or keyword are missing or empty")
            continue

        logger.info("Start processing {} {}".format(specimen_id, keyword))

        # Look for matches
        sample = search_analysis_container([specimen_id])
        if not sample:
            logger.error("no match found for speciment {}"
                         .format(repr(specimen_id)))
            return False

        analyses = sample.getAnalyses()
        if len(analyses) == 0:
            logger.error("No analyses found in sample {}".format(sample.getId()))
            continue

        analyses = [an for an in analyses if an.review_state not in ['retracted', ]]
        logger.info("Found {} active analysis".format(len(analyses)))

        # Construct ASTM order to send to instrument

        logger.info("Preceesed {} {}".format(specimen_id, keyword))

    logger.info("process_query complete")
    return True
