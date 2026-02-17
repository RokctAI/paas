import frappe

@frappe.whitelist(allow_guest=True)
def flow_endpoint():
    """
    Endpoint for WhatsApp Flows.
    """
    return {"status": "success"}

@frappe.whitelist(allow_guest=True)
def hook():
    """
    Webhook for WhatsApp updates.
    """
    return {"status": "success"}
