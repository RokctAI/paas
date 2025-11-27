# Repeating Order API
import frappe

@frappe.whitelist()
def create_repeating_order(original_order: str, start_date: str, cron_pattern: str, end_date: str = None, lang: str = "en"):
    """
    Creates a new repeating order.
    """
    repeating_order = frappe.get_doc({
        "doctype": "Repeating Order",
        "user": frappe.session.user,
        "original_order": original_order,
        "start_date": start_date,
        "cron_pattern": cron_pattern,
        "end_date": end_date,
    })
    repeating_order.insert(ignore_permissions=True)
    return repeating_order.as_dict()

@frappe.whitelist()
def delete_repeating_order(repeating_order_id: str, lang: str = "en"):
    """
    Deletes a repeating order.
    """
    frappe.delete_doc("Repeating Order", repeating_order_id, ignore_permissions=True)
    return {"status": "success"}
