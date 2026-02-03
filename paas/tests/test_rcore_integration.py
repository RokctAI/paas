import frappe
from frappe.tests.utils import FrappeTestCase

class TestRcoreIntegration(FrappeTestCase):
    def setUp(self):
        # Create a test user
        if not frappe.db.exists("User", "test_rcore_user@example.com"):
            self.user = frappe.get_doc({
                "doctype": "User",
                "email": "test_rcore_user@example.com",
                "first_name": "Test",
                "last_name": "Rcore User",
                "roles": [{"role": "Customer"}]
            }).insert(ignore_permissions=True)
        else:
            self.user = frappe.get_doc("User", "test_rcore_user@example.com")
            
        # Create a test customer linked to user
        if not frappe.db.exists("Customer", "Test Rcore Customer"):
            self.customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Rcore Customer",
                "customer_type": "Individual",
                "customer_group": "All Customer Groups",
                "territory": "All Territories",
                "user": self.user.name  # Link to user
            }).insert(ignore_permissions=True)
        else:
            self.customer = frappe.get_doc("Customer", "Test Rcore Customer")
            # Ensure link exists
            if not self.customer.user:
                 self.customer.user = self.user.name
                 self.customer.save(ignore_permissions=True)

    def tearDown(self):
        # Cleanup
        if hasattr(self, "user"):
            frappe.db.delete("Wallet History", {"wallet": ["in", frappe.get_all("Wallet", {"user": self.user.name}, pluck="name")]})
            frappe.db.delete("Wallet", {"user": self.user.name})
            # Clean up Loan Docs too? Maybe later.

    def test_loan_disbursement_wallet_integration(self):
        # 1. Create a Loan Disbursement mock doc
        loan_doc = frappe.get_doc({
            "doctype": "Loan Disbursement",
            "applicant_type": "Customer",
            "applicant": self.customer.name,
            "disbursed_amount": 5000,
            "name": "TEST-LOAN-DISB-001"
        })
        
        # Import from rcore (cross-app call)
        from rcore.rlending.wallet_integration import credit_wallet_on_disbursement
        
        credit_wallet_on_disbursement(loan_doc, "on_submit")
        
        # Verify wallet exists and balance is 5000 (Query by User now)
        wallet = frappe.get_doc("Wallet", {"user": self.user.name})
        self.assertEqual(wallet.balance, 5000)
        
        # Verify history record
        history = frappe.get_all("Wallet History", filters={"wallet": wallet.name}, fields=["transaction_type", "amount"])
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].transaction_type, "Loan Disbursement")
        self.assertEqual(history[0].amount, 5000)

    def test_loan_repayment_wallet_integration(self):
        # 1. Ensure wallet exists with balance
        wallet = frappe.get_doc({
            "doctype": "Wallet",
            "user": self.user.name,
            "balance": 1000
        }).insert(ignore_permissions=True)
        
        from rcore.rlending.wallet_integration import debit_wallet_on_repayment
        
        repayment_doc = frappe.get_doc({
            "doctype": "Loan Repayment",
            "applicant_type": "Customer",
            "applicant": self.customer.name,
            "amount_paid": 200,
            "name": "TEST-LOAN-REPAY-001"
        })
        
        debit_wallet_on_repayment(repayment_doc, "on_submit")
        
        wallet.reload()
        self.assertEqual(wallet.balance, 800)
