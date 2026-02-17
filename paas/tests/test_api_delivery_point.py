# Copyright (c) 2025 ROKCT Holdings
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from paas.api.shop.shop import get_nearest_delivery_points

class TestDeliveryPointAPI(FrappeTestCase):
    def setUp(self):
        # Create a test delivery point
        if not frappe.db.exists("Delivery Point", "Test Delivery Point"):
            self.delivery_point = frappe.get_doc({
                "doctype": "Delivery Point",
                "name": "Test Delivery Point",
                "active": 1,
                "price": 10.0,
                "address": "123 Test Street",
                "latitude": 12.340000,
                "longitude": 56.780000,
            }).insert(ignore_permissions=True)
        else:
            self.delivery_point = frappe.get_doc("Delivery Point", "Test Delivery Point")

    def tearDown(self):
        try:
            self.delivery_point.delete(ignore_permissions=True)
        except Exception:
            pass

    def test_get_nearest_delivery_points(self):
        # Test with coordinates close to the test point
        points = get_nearest_delivery_points(latitude=12.34, longitude=56.78)
        self.assertTrue(isinstance(points, list))
        self.assertTrue(len(points) > 0)
        self.assertEqual(points[0].get("name"), self.delivery_point.name)

    def test_get_nearest_delivery_points_far_away(self):
        # Test with coordinates far from the test point
        points = get_nearest_delivery_points(latitude=40.0, longitude=-74.0)
        self.assertTrue(isinstance(points, list))
        self.assertEqual(len(points), 0)

    def test_get_inactive_delivery_point(self):
        self.delivery_point.active = 0
        self.delivery_point.save(ignore_permissions=True)

        points = get_nearest_delivery_points(latitude=12.34, longitude=56.78)
        self.assertEqual(len(points), 0)

    def test_invalid_parameters(self):
        with self.assertRaises(frappe.exceptions.ValidationError):
            get_nearest_delivery_points(latitude=None, longitude=56.78)
        with self.assertRaises(frappe.exceptions.ValidationError):
            get_nearest_delivery_points(latitude=12.34, longitude=None)
        with self.assertRaises(frappe.exceptions.ValidationError):
            get_nearest_delivery_points(latitude="invalid", longitude="invalid")
