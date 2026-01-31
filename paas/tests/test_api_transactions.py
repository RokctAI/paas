# Copyright (c) 2025 ROKCT Holdings
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from paas.api import get_user_transactions

class TestTransactionsAPI(FrappeTestCase):
    def setUp(self):
        # Create a test user
        if not frappe.db.exists("User", "test_transactions@example.com"):
            self.test_user = frappe.get_doc({
                "doctype": "User",
                "email": "test_transactions@example.com",
                "first_name": "Test",
                "last_name": "Transactions",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
        else:
            self.test_user = frappe.get_doc("User", "test_transactions@example.com")
        self.test_user.add_roles("System Manager")

        # Create a test order to associate with a transaction
        if not frappe.db.exists("Order", {"user": self.test_user.name, "status": "New"}):
            self.order = frappe.get_doc({
                "doctype": "Order",
                "user": self.test_user.name,
                "status": "New"
            }).insert(ignore_permissions=True)
        else:
            self.order = frappe.get_doc("Order", {"user": self.test_user.name, "status": "New"})

        # Create a transaction for the user
        if not frappe.db.exists("Transaction", {"user": self.test_user.name, "payable_id": self.order.name}):
            self.transaction = frappe.get_doc({
                "doctype": "Transaction",
                "payable_type": "Order",
                "payable_id": self.order.name,
                "user": self.test_user.name,
                "price": 50.0,
                "status": "Paid",
                "type": "model"
            }).insert(ignore_permissions=True)
        else:
            self.transaction = frappe.get_doc("Transaction", {"user": self.test_user.name, "payable_id": self.order.name})

        # Log in as the test user
        frappe.set_user(self.test_user.name)

    def tearDown(self):
        # Log out
        frappe.set_user("Administrator")
        self.transaction.delete(ignore_permissions=True)
        self.order.delete(ignore_permissions=True)
        self.test_user.delete(ignore_permissions=True)

    def test_get_user_transactions_pagination(self):
        # Create a second transaction
        if not frappe.db.exists("Transaction", {"user": self.test_user.name, "price": 25.0}):
            frappe.get_doc({
                "doctype": "Transaction",
                "payable_type": "Order",
                "payable_id": self.order.name,
                "user": self.test_user.name,
                "price": 25.0,
                "status": "Paid",
                "type": "model"
            }).insert(ignore_permissions=True)

        # Get the first page with a limit of 1
        transactions = get_user_transactions(limit_page_length=1)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].get("price"), 25.0) # It's ordered by creation desc

        # Get the second page
        transactions = get_user_transactions(limit_start=1, limit_page_length=1)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].get("price"), 50.0)

