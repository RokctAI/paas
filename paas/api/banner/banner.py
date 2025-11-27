# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def get_ads(page: int = 1):
    """
    Fetches a paginated list of banners that are marked as ads.
    """
    return frappe.get_all(
        "Banner",
        filters={"is_ad": 1, "is_active": 1},
        fields=["name", "title", "image", "link"],
        limit_page_length=10,
        limit_start=(page - 1) * 10,
    )

@frappe.whitelist()
def get_ad(id: str):
    """
    Fetches a single banner that is marked as an ad.
    """
    return frappe.get_doc("Banner", id)

@frappe.whitelist()
def like_banner(id: str):
    """
    Increments the 'likes' count on a banner.
    """
    banner = frappe.get_doc("Banner", id)
    banner.likes = banner.likes + 1
    banner.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "likes": banner.likes}
