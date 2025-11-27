import frappe
import json
from frappe.utils import now_datetime

@frappe.whitelist()
def create_blog(data):
    """
    Creates a new Blog post.
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    doc = frappe.get_doc({
        "doctype": "Blog",
        **data
    })
    doc.insert()
    return doc.as_dict()

@frappe.whitelist(allow_guest=True)
def get_blogs(type=None, limit=10, start=0):
    """
    Retrieves Blogs, optionally filtered by type.
    """
    filters = {"active": 1, "published_at": ["<=", now_datetime()]}
    if type:
        filters["type"] = type
        
    return frappe.get_list("Blog", 
        filters=filters, 
        fields=["name", "title", "short_description", "img", "published_at", "author", "type"],
        order_by="published_at desc",
        start=start,
        page_length=limit
    )

@frappe.whitelist(allow_guest=True)
def get_blog_details(name):
    """
    Retrieves full details of a Blog post.
    """
    return frappe.get_doc("Blog", name).as_dict()

@frappe.whitelist()
def update_blog(name, data):
    """
    Updates a Blog post.
    """
    if isinstance(data, str):
        data = json.loads(data)
        
    doc = frappe.get_doc("Blog", name)
    doc.update(data)
    doc.save()
    return doc.as_dict()

@frappe.whitelist()
def delete_blog(name):
    """
    Deletes a Blog post.
    """
    frappe.delete_doc("Blog", name)
    return {"status": "success"}
