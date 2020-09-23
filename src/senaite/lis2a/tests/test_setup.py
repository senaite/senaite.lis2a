# -*- coding: utf-8 -*-

from senaite.lis2a import PRODUCT_NAME
from senaite.lis2a.tests.base import SimpleTestCase


class TestSetup(SimpleTestCase):
    """Test Setup
    """

    def test_is_senaite_lis2a_installed(self):
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled(PRODUCT_NAME))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
