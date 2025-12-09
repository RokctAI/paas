app_name = "paas"
app_title = "PaaS"
app_publisher = "ROKCT INTELLIGENCE (PTY) LTD"
app_description = "PaaS App for Rokct"
app_email = "admin@rokct.ai"
app_license = "AGPL-3.0"

# Installation
# ------------
before_install = "paas.install.check_site_role"
after_install = "paas.install.run_seeders"

# Authentication
# --------------
auth_hooks = ["paas.api.auth.auth.validate"]

# Scheduler Events
# ----------------
import frappe

def get_safe_scheduler_events():
	"""
	Safely get scheduler events by checking if frappe.conf exists.
	This prevents crashes during installation where frappe.conf is not yet available.
	"""
	# This function is called at import time, so we must be defensive.
	if not hasattr(frappe, "conf") or not frappe.conf:
		return {}

	app_role = frappe.conf.get("app_role", "tenant")
	events = {}
	
	if app_role == "tenant":
		# PaaS tasks only run on tenant sites
		events = {
			"hourly": [
				"paas.tasks.process_repeating_orders"
			],
			"daily": [
				"paas.tasks.remove_expired_stories"
			]
		}
	
	return events

scheduler_events = get_safe_scheduler_events()

# Whitelisted Methods
# -------------------
whitelisted_methods = {
    # Notification APIs
    "paas.api.get_notification_types": "paas.api.get_notification_types",
    "paas.api.get_user_notification_preferences": "paas.api.get_user_notification_preferences",
    "paas.api.set_user_notification_preference": "paas.api.set_user_notification_preference",
    "paas.api.get_notification_logs": "paas.api.get_notification_logs",
    "paas.api.mark_notification_logs_as_read": "paas.api.mark_notification_logs_as_read",

    # Translation APIs
    "paas.api.translation.get_mobile_translations": "paas.api.translation.get_mobile_translations",
    "paas.api.translation.get_translations_paginate": "paas.api.translation.get_translations_paginate",
    "paas.api.translation.create_translation": "paas.api.translation.create_translation",
    "paas.api.translation.update_translation": "paas.api.translation.update_translation",
    "paas.api.translation.delete_translation": "paas.api.translation.delete_translation",
    "paas.api.translation.drop_all_translations": "paas.api.translation.drop_all_translations",
    "paas.api.translation.truncate_translations": "paas.api.translation.truncate_translations",
    "paas.api.translation.restore_all_translations": "paas.api.translation.restore_all_translations",
    "paas.api.translation.import_translations": "paas.api.translation.import_translations",
    "paas.api.translation.export_translations": "paas.api.translation.export_translations",
    "paas.api.translation.handle_translations_root": "paas.api.translation.handle_translations_root",
    "paas.api.translation.handle_translation_resource": "paas.api.translation.handle_translation_resource"
}

# Fixtures
# ---------
fixtures = [
    {"dt": "DocType", "filters": [["name", "=", dt_name]]}
    for dt_name in [
        "Kitchen Translation",
        "Subscription",
        "Wallet",
        "Brand",
        "Kitchen",
        "Menu",
        "Parcel Order Item",
        "Parcel Category",
        "Parcel Option",
        "Shop Ads Package",
        "Membership",
        "Shop Booking Closed Date",
        "Wallet History",
        "Shop Cart",
        "Coupon Translation",
        "Point",
        "Order Item",
        "User Shop",
        "Seller Payout",
        "Story",
        "Shop Unit",
        "Coupon",
        "Ads Package",
        "Repeating Order",
        "Shop Booking Working Day",
        "Branch",
        "Shop Gallery",
        "Delivery Vehicle Type",
        "Shop Deliveryman Settings",
        "Menu Item",
        "Loan Contract",
        "Product Extra Value",
        "Shop Closed Day",
        "Shop Cart User",
        "Delivery Point",
        "Shop Subscription",
        "Shop Working Day",
        "Shop Category",
        "FAQ Category",
        "Shop Tag",
        "Booking",
        "User Booking",
        "Category Translation",
        "Seller",
        "DeliveryMan Settings",
        "Shop Section",
        "Ticket",
        "Deliveryman Delivery Zone",
        "Coupon Usage",
        "Flutterwave Settings",
        "Device Token",
        "Parcel Order",
        "Email Subscription",
        "Shop Ban",
        "User Membership",
        "Payout",
        "Payment Payload",
        "Combo",
        "User Address",
        "Parcel Order Setting",
        "Banner",
        "Order",
        "Product Translation",
        "Shop Bonus",
        "Cashback Rule",
        "Combo Item",
        "Permission Settings",
        "Project Settings",
        "Email Settings",
        "Request Model",
        "Table",
        "Category",
        "FAQ",
        "Invitation",
        "Product Extra Group",
        "Tag",
        "Order Refund",
        "Loan Application",
        "Saved Card",
        "Ad",
        "Global Settings",
        "Parcel Review",
        "Loan Eligibility Check",
        "Cart User",
        "Google User",
        "Password Reset",
        "Tip",
        "Referral",
        "Scoring Rule",
        "Scorecard Metric",
        "Scorecard",
        "Shop",
        "Eligible Plan",
        "Career Category",
        "Career",
        "Delivery Zone",
        "Delivery Zone Coordinate",
        "Order Status",
        "Receipt",
        "Receipt Stock",
        "Receipt Instruction",
        "Receipt Ingredient",
        "Receipt Nutrition",
        "User Cart",
        "Cart Detail",
        "Cart",
        "Review",
        "Driver Location",
        "PaaS Translation",
        "Settings",
        "Referral Campaign",
        "Referral Campaign Translation",
    ]
]

# Website Route Rules
website_route_rules = [
    {"from_route": "/.well-known/assetlinks.json", "to_route": "paas.api.app_links.get_assetlinks"},
    {"from_route": "/.well-known/apple-app-site-association", "to_route": "paas.api.app_links.get_apple_app_site_association"},
]
