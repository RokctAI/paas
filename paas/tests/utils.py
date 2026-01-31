import frappe

def before_tests():
    """
    Setup required data before running tests.
    """
    create_warehouse_types()
    create_customer_groups()
    create_item_groups()
    create_territories()

def create_warehouse_types():
    if not frappe.db.exists("Warehouse Type", "Transit"):
        frappe.get_doc({
            "doctype": "Warehouse Type",
            "name": "Transit"
        }).insert(ignore_permissions=True)

def create_customer_groups():
    if not frappe.db.exists("Customer Group", "All Customer Groups"):
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "All Customer Groups",
            "is_group": 1,
            "parent_customer_group": "" 
        }).insert(ignore_permissions=True)

def create_item_groups():
    if not frappe.db.exists("Item Group", "All Item Groups"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "All Item Groups",
            "is_group": 1,
            "parent_item_group": ""
        }).insert(ignore_permissions=True)

def create_territories():
    if not frappe.db.exists("Territory", "All Territories"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "All Territories",
            "is_group": 1,
            "parent_territory": ""
        }).insert(ignore_permissions=True)
