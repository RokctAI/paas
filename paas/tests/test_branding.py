# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt

import unittest
from unittest.mock import MagicMock, patch
import frappe
from paas.branding import get_paas_branding, get_paas_brand_html

class TestBranding(unittest.TestCase):
    def setUp(self):
        # Patch frappe methods
        self.get_value_patch = patch('frappe.db.get_value')
        self.get_doc_patch = patch('frappe.get_doc')
        self.get_single_patch = patch('frappe.get_single')
        self.defaults_patch = patch('frappe.defaults.get_user_default', return_value="Test Company")

        self.mock_get_value = self.get_value_patch.start()
        self.mock_get_doc = self.get_doc_patch.start()
        self.mock_get_single = self.get_single_patch.start()
        self.mock_defaults = self.defaults_patch.start()

    def tearDown(self):
        self.get_value_patch.stop()
        self.get_doc_patch.stop()
        self.get_single_patch.stop()
        self.defaults_patch.stop()

    def test_get_paas_branding_no_subscription(self):
        # Mock no subscription found
        self.mock_get_value.return_value = None

        result = get_paas_branding()
        self.assertEqual(result, {'enabled': False})

    def test_get_paas_branding_no_paas_module(self):
        # Mock subscription found but no PaaS module
        self.mock_get_value.return_value = MagicMock(subscription_plan='Basic Plan')

        mock_plan = MagicMock()
        mock_plan.modules = [MagicMock(module_name='Other')]
        self.mock_get_doc.return_value = mock_plan

        result = get_paas_branding()
        self.assertEqual(result, {'enabled': False})

    def test_get_paas_branding_enabled_defaults(self):
        # Mock subscription with PaaS module
        self.mock_get_value.return_value = MagicMock(subscription_plan='Pro Plan')

        mock_plan = MagicMock()
        mock_plan.modules = [MagicMock(module_name='PaaS')]
        self.mock_get_doc.return_value = mock_plan

        # Mock Settings (empty/defaults)
        mock_settings = MagicMock()
        mock_settings.logo = None
        mock_settings.favicon = None
        mock_settings.project_title = None
        self.mock_get_single.return_value = mock_settings

        result = get_paas_branding()
        self.assertEqual(result['enabled'], True)
        self.assertEqual(result['logo'], '/assets/rokct/images/logo.svg')
        self.assertEqual(result['app_name'], 'ROKCT')

    def test_get_paas_branding_enabled_custom(self):
        # Mock subscription with PaaS module
        self.mock_get_value.return_value = MagicMock(subscription_plan='Pro Plan')

        mock_plan = MagicMock()
        mock_plan.modules = [MagicMock(module_name='PaaS')]
        self.mock_get_doc.return_value = mock_plan

        # Mock Settings with values
        mock_settings = MagicMock()
        mock_settings.logo = '/files/my_logo.png'
        mock_settings.favicon = '/files/my_favicon.ico'
        mock_settings.project_title = 'My App'
        self.mock_get_single.return_value = mock_settings

        result = get_paas_branding()
        self.assertEqual(result['enabled'], True)
        self.assertEqual(result['logo'], '/files/my_logo.png')
        self.assertEqual(result['app_name'], 'My App')

    def test_get_paas_brand_html_disabled(self):
        # Mock get_paas_branding returning disabled
        with patch('paas.branding.get_paas_branding') as mock_get_branding:
            mock_get_branding.return_value = {'enabled': False}
            result = get_paas_brand_html()
            self.assertEqual(result, "")

    def test_get_paas_brand_html_enabled(self):
        # Mock get_paas_branding returning enabled
        with patch('paas.branding.get_paas_branding') as mock_get_branding:
            mock_get_branding.return_value = {
                'enabled': True,
                'logo': '/logo.png',
                'app_name': 'Test App'
            }
            result = get_paas_brand_html()
            self.assertIn("frappe.ready(function()", result)
            self.assertIn("/logo.png", result)
            self.assertIn("Test App", result)
