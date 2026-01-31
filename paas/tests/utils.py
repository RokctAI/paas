import frappe

def before_tests():
    """
    Setup required data before running tests.
    """
    create_warehouse_types()

def create_warehouse_types():
    if not frappe.db.exists("Warehouse Type", "Transit"):
        frappe.get_doc({
            "doctype": "Warehouse Type",
            "name": "Transit"
        }).insert(ignore_permissions=True)
