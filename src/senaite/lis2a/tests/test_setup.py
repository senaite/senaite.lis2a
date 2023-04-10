# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import get_installer
from senaite.lis2a import PRODUCT_NAME
from senaite.lis2a.tests.base import SimpleTestCase


class TestSetup(SimpleTestCase):
    """Test Setup
    """

    def test_is_senaite_lis2a_installed(self):
        qi = get_installer(self.portal)
        self.assertTrue(qi.isProductInstalled(PRODUCT_NAME))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
