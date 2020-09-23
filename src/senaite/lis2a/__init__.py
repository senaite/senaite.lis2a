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

import logging

from Products.Archetypes.atapi import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import ContentInit
from senaite.lis2a.interfaces import ISenaiteLis2aLayer

PRODUCT_NAME = "senaite.lis2a"
PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)
UNINSTALL_PROFILE_ID = "profile-{}:uninstall".format(PRODUCT_NAME)

logger = logging.getLogger(PRODUCT_NAME)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE LIS2A Customization package ***")

    types = listTypes(PRODUCT_NAME)
    content_types, constructors, ftis = process_types(types, PRODUCT_NAME)

    # Register each type with it's own Add permission
    # use ADD_CONTENT_PERMISSION as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (PRODUCT_NAME, atype.portal_type)
        ContentInit(kind,
                    content_types=(atype,),
                    permission=AddPortalContent,
                    extra_constructors=(constructor, ),
                    fti=ftis,
                    ).initialize(context)


def is_installed():
    """Returns whether the product is installed or not
    """
    from bika.lims import api
    request = api.get_request()
    return ISenaiteLis2aLayer.providedBy(request)
