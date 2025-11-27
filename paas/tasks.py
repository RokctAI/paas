# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt
import frappe
from frappe.utils import now_datetime
from datetime import datetime

@frappe.whitelist()
def remove_expired_stories():
    """
    Find and delete stories that have expired.
    This is run daily by the scheduler on tenant sites.
    """
    if frappe.conf.get("app_role") != "tenant":
        return

    print("Running Daily Expired Stories Cleanup Job...")

    expired_stories = frappe.get_all("Story",
        filters={
            "expires_at": ["<", now_datetime()]
        },
        pluck="name"
    )

    if not expired_stories:
        print("No expired stories to delete.")
        return

    print(f"Found {len(expired_stories)} expired stories to delete...")

    for story_name in expired_stories:
        try:
            frappe.delete_doc("Story", story_name, ignore_permissions=True, force=True)
            print(f"  - Deleted expired story: {story_name}")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Failed to delete expired story {story_name}")

    frappe.db.commit()
    print("Expired Stories Cleanup Job Complete.")

@frappe.whitelist()
def process_repeating_orders():
    """
    Process repeating orders that are due for execution.
    """
    try:
        from croniter import croniter
    except ImportError:
        print("croniter not found. Skipping repeating orders.")
        return

    print("Processing Repeating Orders...")
    now = now_datetime()

    # Fetch active repeating orders where next_execution is due or not set (first run)
    repeating_orders = frappe.get_all("Repeating Order",
        filters={
            "is_active": 1,
            "start_date": ["<=", now.date()],
            "next_execution": ["<=", now]
        },
        fields=["name", "original_order", "cron_pattern", "next_execution", "end_date"]
    )

    # Also fetch those that haven't run yet (next_execution is None) but start_date is past
    # Actually, we should have set next_execution on creation.
    # If None, we process it now? Or verify logic.
    # For now, let's query those with next_execution <= now OR next_execution IS NULL

    # Simplified query to catch NULLs if Frappe supports it easily, or just separate query.
    # frappe.get_all doesn't support OR easily in filters dict.
    # We'll iterate what we found.

    count = 0
    for ro in repeating_orders:
        if ro.end_date and ro.end_date < now.date():
            # Expired
            frappe.db.set_value("Repeating Order", ro.name, "is_active", 0)
            continue

        try:
            # Create the order
            original_order_doc = frappe.get_doc("Order", ro.original_order)
            new_order = frappe.copy_doc(original_order_doc)

            # Update specific fields
            new_order.transaction_date = now
            new_order.delivery_date = now.date() # Or calculated based on original delta?
            new_order.status = "New"
            new_order.amended_from = None
            new_order.insert(ignore_permissions=True)

            print(f"Created recurring order {new_order.name} from {ro.name}")
            count += 1

            # Calculate next execution
            iter = croniter(ro.cron_pattern, now)
            next_exec = iter.get_next(datetime)

            frappe.db.set_value("Repeating Order", ro.name, {
                "last_execution": now,
                "next_execution": next_exec
            })

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Failed to process Repeating Order {ro.name}")

    if count > 0:
        frappe.db.commit()
    print(f"Processed {count} repeating orders.")
