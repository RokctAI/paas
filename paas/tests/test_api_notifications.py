# Copyright (c) 2025 ROKCT Holdings
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from paas.api import get_user_notifications

class TestNotificationsAPI(FrappeTestCase):
    def setUp(self):
        # Create a test user
        if not frappe.db.exists("User", "test_notifications@example.com"):
            self.test_user = frappe.get_doc({
                "doctype": "User",
                "email": "test_notifications@example.com",
                "first_name": "Test",
                "last_name": "Notifications",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
        else:
            self.test_user = frappe.get_doc("User", "test_notifications@example.com")
        self.test_user.add_roles("System Manager")

        # Create notification type if not exists (Usually standard, but Alert might be missing)
        if not frappe.db.exists("Notification Type", "Alert"):
             # Assuming 'Notification Type' is a doctype, or it's just a select/link options.
             # The error was LinkValidationError, link to 'Notification Type'.
             # Standard Frappe actually doesn't use 'Notification Type' link in Notification Log usually?
             # 'type' is a Select in standard Notification Log.
             # But here key is 'notification_type', likely custom or mapped.
             pass 

        # If 'notification_type' is a Link field to 'Notification Type' DocType:
        # We need to construct it. But let's check if the DocType exists first.
        # However, to be safe, standard Notification Log uses 'type' (Select).
        # PaaS seems to use 'notification_type'. Inspecting error: "Could not find Notification Type: Alert"
        # imply it is a Link.
        
        # Create 'Alert' Notification Type if it doesn't exist
        # We handle the case where Notification Type might not be a standard doctype in some envs
        # Warning: Verify if Notification Type exists as a DocType first
        if frappe.db.exists("DocType", "Notification Type"):
            try:
                if not frappe.db.exists("Notification Type", "Alert"):
                    frappe.get_doc({
                        "doctype": "Notification Type",
                        "name": "Alert",
                        "type": "Alert" # Some versions use 'type' field
                    }).insert(ignore_permissions=True)
            except frappe.DuplicateEntryError:
                pass

        # Create a notification log for the user
        if not frappe.db.exists("Notification Log", {"subject": "Test Notification", "for_user": self.test_user.name}):
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": "Test Notification",
                "for_user": self.test_user.name,
                "user": self.test_user.name,
                "notification_type": "Alert",
                "message": "Test Message",
                "document_type": "User",
                "document_name": self.test_user.name
            }).insert(ignore_permissions=True)

        # Log in as the test user
        frappe.set_user(self.test_user.name)

    def tearDown(self):
        # Log out
        frappe.set_user("Administrator")
        frappe.db.delete("Notification Log", {"for_user": self.test_user.name})
        if frappe.db.exists("User", self.test_user.name):
            try:
                self.test_user.delete(ignore_permissions=True)
            except frappe.exceptions.LinkExistsError:
                frappe.db.set_value("User", self.test_user.name, "enabled", 0)

    def test_get_user_notifications(self):
        notifications = get_user_notifications()
        self.assertTrue(isinstance(notifications, list))
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].get("subject"), "Test Notification")

