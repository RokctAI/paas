import frappe

@frappe.whitelist()
def get_story(story_id: str):
    """
    Retrieves a story by ID.
    """
    return frappe.get_doc("Story", story_id).as_dict()
