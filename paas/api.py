# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt
# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import frappe
from paas.utils import check_subscription_feature, get_subscription_details
from paas.api.shop.shop import get_shops, get_shop_details, search_shops, get_shop_types
from paas.api.product.product import (
    get_products,
    most_sold_products,
    get_discounted_products,
    get_products_by_ids,
    get_product_by_uuid,
    get_product_by_slug,
    read_product_file,
    get_product_reviews,
    order_products_calculate,
    get_products_by_brand,
    products_search,
    get_products_by_category,
    get_products_by_shop,
    add_product_review,
    get_product_history
)
from paas.api.category.category import (
    get_categories,
    get_category_types,
    get_children_categories,
    search_categories,
    get_category_by_uuid,
    create_category,
    update_category,
    delete_category
)
from paas.api.brand.brand import (
    get_brands,
    get_brand_by_uuid,
    create_brand,
    update_brand,
    delete_brand
)
from paas.api.user.user import (
    logout,
    check_phone,
    send_phone_verification_code,
    verify_phone_code,
    register_user,
    forgot_password,
    get_user_membership,
    get_user_membership_history,
    get_user_parcel_orders,
    get_user_parcel_order,
    get_user_addresses,
    get_user_address,
    add_user_address,
    update_user_address,
    delete_user_address,
    get_user_invites,
    create_invite,
    update_invite_status,
    get_user_wallet,
    get_wallet_history,
    export_orders,
    register_device_token,
    get_user_transactions,
    get_user_shop,
    update_seller_shop,
    get_user_request_models,
    create_request_model,
    get_user_tickets,
    get_user_ticket,
    create_ticket,
    reply_to_ticket,
    update_user_profile,
    get_user_order_refunds,
    create_order_refund,
    get_user_notifications,
    login_with_google,
    forgot_password_confirm,
    get_user_profile,
)
from paas.api.payment.payment import (
    get_payment_gateways,
    get_payment_gateway,
    initiate_flutterwave_payment,
    flutterwave_callback,
    get_payfast_settings,
    handle_payfast_callback,
    process_payfast_token_payment,
    save_payfast_card,
    get_saved_payfast_cards,
    delete_payfast_card,
    handle_paypal_callback,
    initiate_paypal_payment,
    initiate_paystack_payment,
    handle_paystack_callback,
    log_payment_payload,
    handle_stripe_webhook,
)
from paas.api.cart.cart import (
    get_cart,
    add_to_cart,
    remove_from_cart,
    remove_product_cart,
    calculate_cart_totals,
)
from paas.api.order.order import (
    create_order,
    list_orders,
    get_order_details,
    update_order_status,
    add_order_review,
    cancel_order,
    get_order_statuses,
    get_calculate,
)
from paas.api.receipt.receipt import (
    get_receipts,
    get_receipt,
)
from paas.api.blog.blog import (
    get_admin_blogs,
    create_admin_blog,
    update_admin_blog,
    delete_admin_blog,
    get_blogs,
    get_blog,
)
from paas.api.career.career import (
    get_careers,
    get_career,
    get_admin_careers,
)
from paas.api.page.page import (
    get_page,
    get_admin_pages,
    get_admin_web_page,
    update_admin_web_page,
)
from paas.api.delivery.delivery import (
    is_point_in_polygon,
    get_delivery_zone_by_shop,
    check_delivery_zone,
    get_delivery_points,
    get_delivery_point,
)
from paas.api.branch.branch import (
    get_branches,
    get_branch,
    create_branch,
    update_branch,
    delete_branch,
)
from paas.api.parcel.parcel import (
    create_parcel_order,
    get_parcel_orders,
    update_parcel_status,
)
from paas.api.parcel_option.parcel_option import (
    get_parcel_options,
    create_parcel_option,
    update_parcel_option,
    delete_parcel_option,
)
from paas.api.booking.booking import (
    create_booking,
    get_booking,
    update_booking,
    delete_booking,
    create_shop_section,
    get_shop_section,
    update_shop_section,
    delete_shop_section,
    create_table,
    get_table,
    update_table,
    delete_table,
    get_user_bookings,
    update_user_booking_status,
    get_shop_bookings,
    get_shop_sections_for_booking,
    get_tables_for_section,
    create_user_booking,
    get_my_bookings,
    cancel_my_booking,
    get_shop_user_bookings,
    update_shop_user_booking_status,
    manage_shop_booking_working_days,
    manage_shop_booking_closed_dates,
)
from paas.api.subscription.subscription import (
    create_subscription,
    get_subscription,
    list_subscriptions,
    update_subscription,
    delete_subscription,
    assign_subscription_to_shop,
    get_shop_subscriptions,
    update_shop_subscription,
    cancel_shop_subscription,
    get_my_shop_subscription,
    subscribe_my_shop,
)
from paas.api.admin_reports.admin_reports import (
    get_admin_statistics,
    get_multi_company_sales_report,
    get_admin_report,
    get_all_wallet_histories,
    get_all_transactions,
    get_all_seller_payouts,
    get_all_shop_bonuses,
)
from paas.api.admin_management.admin_management import (
    get_all_shops,
    create_shop,
    update_shop,
    delete_shop,
    get_all_users,
    get_all_roles,
)
from paas.api.admin_content.admin_content import (
    get_admin_stories,
    get_admin_banners,
    create_admin_banner,
    update_admin_banner,
    delete_admin_banner,
    get_admin_faqs,
    create_admin_faq,
    update_admin_faq,
    delete_admin_faq,
    get_admin_faq_categories,
    create_admin_faq_category,
    update_admin_faq_category,
    delete_admin_faq_category,
)
from paas.api.admin_records.admin_records import (
    get_all_orders,
    get_all_parcel_orders,
    get_all_reviews,
    update_admin_review,
    delete_admin_review,
    get_all_tickets,
    update_admin_ticket,
    get_all_order_refunds,
    update_admin_order_refund,
    get_all_notifications,
    get_all_bookings,
    create_booking,
    update_booking,
    delete_booking,
    get_all_request_models,
    get_all_order_statuses,
)
from paas.api.admin_settings.admin_settings import (
    get_all_languages,
    update_language,
    get_all_currencies,
    update_currency,
    get_email_settings,
    update_email_settings,
    get_all_email_templates,
    update_email_template,
    get_email_subscriptions,
    create_email_subscription,
    delete_email_subscription,
)
from paas.api.admin_data.admin_data import (
    get_all_units,
    get_all_tags,
    get_all_points,
    create_point,
    update_point,
    delete_point,
    get_all_translations,
    get_all_referrals,
    create_referral,
    delete_referral,
    get_all_shop_tags,
    get_all_product_extra_groups,
    get_all_product_extra_values,
)
from paas.api.admin_logistics.admin_logistics import (
    get_deliveryman_global_settings,
    update_deliveryman_global_settings,
    get_parcel_order_settings,
    create_parcel_order_setting,
    update_parcel_order_setting,
    delete_parcel_order_setting,
    get_all_delivery_zones,
    get_delivery_vehicle_types,
    create_delivery_vehicle_type,
    update_delivery_vehicle_type,
    delete_delivery_vehicle_type,
    get_all_delivery_man_delivery_zones,
    get_all_shop_working_days,
    get_all_shop_closed_days,
)
from paas.api.seller_shop_settings.seller_shop_settings import (
    get_seller_shop_working_days,
    update_seller_shop_working_days,
    get_seller_shop_closed_days,
    add_seller_shop_closed_day,
    delete_seller_shop_closed_day,
    get_shop_users,
    add_shop_user,
    remove_shop_user,
    get_seller_branches,
    create_seller_branch,
    update_seller_branch,
    delete_seller_branch,
    get_seller_deliveryman_settings,
    update_seller_deliveryman_settings,
)
from paas.api.seller_marketing.seller_marketing import (
    get_seller_coupons,
    create_seller_coupon,
    update_seller_coupon,
    delete_seller_coupon,
    get_seller_discounts,
    create_seller_discount,
    update_seller_discount,
    delete_seller_discount,
    get_seller_banners,
    create_seller_banner,
    update_seller_banner,
    delete_seller_banner,
    get_ads_packages,
    get_seller_shop_ads_packages,
    purchase_shop_ads_package,
)
from paas.api.seller_operations.seller_operations import (
    get_seller_kitchens,
    create_seller_kitchen,
    update_seller_kitchen,
    delete_seller_kitchen,
    get_seller_inventory_items,
    adjust_seller_inventory,
    get_seller_menus,
    get_seller_menu,
    create_seller_menu,
    update_seller_menu,
    delete_seller_menu,
    get_seller_receipts,
    create_seller_receipt,
    update_seller_receipt,
    delete_seller_receipt,
    get_seller_combos,
    get_seller_combo,
    create_seller_combo,
    update_seller_combo,
    delete_seller_combo,
)
from paas.api.seller_reports.seller_reports import (
    get_seller_statistics,
    get_seller_sales_report,
)
from paas.api.seller_order.seller_order import (
    get_seller_orders,
    get_seller_order_refunds,
    update_seller_order_refund,
    get_seller_reviews,
)
from paas.api.seller_product.seller_product import (
    get_seller_products,
    create_seller_product,
    update_seller_product,
    delete_seller_product,
    get_seller_categories,
    create_seller_category,
    update_seller_category,
    delete_seller_category,
    get_seller_brands,
    create_seller_brand,
    update_seller_brand,
    delete_seller_brand,
    get_seller_extra_groups,
    create_seller_extra_group,
    update_seller_extra_group,
    delete_seller_extra_group,
    get_seller_extra_values,
    create_seller_extra_value,
    update_seller_extra_value,
    delete_seller_extra_value,
    get_seller_units,
    create_seller_unit,
    update_seller_unit,
    delete_seller_unit,
    get_seller_tags,
    create_seller_tag,
    update_seller_tag,
    delete_seller_tag,
)
from paas.api.seller_payout.seller_payout import (
    get_seller_payouts,
)
from paas.api.seller_bonus.seller_bonus import (
    get_seller_bonuses,
)
from paas.api.seller_story.seller_story import (
    get_seller_stories,
    create_seller_story,
    update_seller_story,
    delete_seller_story,
)
from paas.api.seller_delivery_zone.seller_delivery_zone import (
    get_seller_delivery_zones,
    get_seller_delivery_zone,
    create_seller_delivery_zone,
    update_seller_delivery_zone,
    delete_seller_delivery_zone,
)
from paas.api.seller_invites.seller_invites import (
    get_seller_invites,
)
from paas.api.seller_transactions.seller_transactions import (
    get_seller_transactions,
    get_seller_shop_payments,
    get_seller_payment_to_partners,
)
from paas.api.seller_shop_gallery.seller_shop_gallery import (
    get_seller_shop_galleries,
    create_seller_shop_gallery,
    delete_seller_shop_gallery,
)
from paas.api.seller_customer_management.seller_customer_management import (
    get_seller_request_models,
    get_seller_customer_addresses,
)
from paas.api.seller_logistics.seller_logistics import (
    get_seller_delivery_man_delivery_zones,
    adjust_seller_inventory,
)
from paas.api.delivery_man.delivery_man import (
    get_deliveryman_orders,
    get_deliveryman_parcel_orders,
    get_deliveryman_settings,
    update_deliveryman_settings,
    get_deliveryman_statistics,
    get_banned_shops,
    get_payment_to_partners,
    get_deliveryman_order_report,
    get_deliveryman_delivery_zones,
)
from paas.api.waiter.waiter import (
    get_waiter_orders,
    get_waiter_order_report,
)
from paas.api.cook.cook import (
    get_cook_orders,
    get_cook_order_report,
)
from paas.api.notification.notification import (
    send_push_notification,
)
from paas.api.coupon.coupon import check_coupon
from paas.api.system.system import (
    get_weather,
    api_status,
    get_languages,
    get_currencies,
)
from paas.api.remote_config import get_remote_config
from paas.whatsapp.api import webhook as whatsapp_webhook
from rokct.lending.api import (
    create_loan_application as _create_loan_application,
    disburse_loan as _disburse_loan,
    get_my_loan_applications as _get_my_loan_applications,
    request_payout as _request_payout,
)

@frappe.whitelist()
def create_loan_application(applicant_type, applicant, loan_product, loan_amount, income=0, total_expenses=0, skip_documents=0):
    """
    Proxy for creating a loan application via Rokct Lending logic.
    """
    return _create_loan_application(applicant_type, applicant, loan_product, loan_amount, income, total_expenses, skip_documents)

@frappe.whitelist()
def get_my_loan_applications():
    """
    Proxy for retrieving the current user's loan applications.
    """
    from rokct.lending.api import get_my_loan_applications as _get_apps
    return _get_apps()

@frappe.whitelist()
def disburse_loan(loan_application):
    """
    Proxy for disbursing/withdrawing an approved loan.
    """
    return _disburse_loan(loan_application)

@frappe.whitelist()
def request_payout(loan_application):
    """
    Proxy for requesting a payout of withdrawable funds.
    """
    return _request_payout(loan_application)

@frappe.whitelist(allow_guest=True)
def whatsapp_hook():
    return whatsapp_webhook()

@frappe.whitelist(allow_guest=True)
def whatsapp_flow_endpoint():
    # Helper to route to the data endpoint
    from paas.whatsapp.api import whatsapp_flow_data
    return whatsapp_flow_data()
from paas.api.repeating_order import create_repeating_order, delete_repeating_order
from paas.api.payment.payment import (
    get_saved_cards as _get_saved_cards,
    tokenize_card as _tokenize_card,
    delete_card as _delete_card,
    process_direct_card_payment as _process_direct_card_payment,
    process_token_payment as _process_token_payment,
    process_wallet_top_up as _process_wallet_top_up
)

@frappe.whitelist()
def get_saved_cards():
    return _get_saved_cards()

@frappe.whitelist()
def tokenize_card(card_number, card_holder, expiry_date, cvc):
    return _tokenize_card(card_number, card_holder, expiry_date, cvc)

@frappe.whitelist()
def delete_card(card_name):
    return _delete_card(card_name)

@frappe.whitelist()
def process_direct_card_payment(order_id, card_number, card_holder, expiry_date, cvc, save_card=False):
    return _process_direct_card_payment(order_id, card_number, card_holder, expiry_date, cvc, save_card)

@frappe.whitelist()
def process_token_payment(order_id, token):
    return _process_token_payment(order_id, token)

@frappe.whitelist()
def process_wallet_top_up(amount):
    return _process_wallet_top_up(amount)

@frappe.whitelist()
def get_nearby_shops(latitude: float, longitude: float, radius_km: float = 10, lang: str = "en"):
    """
    Retrieves a list of shops within a given radius.
    """
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Radius of Earth in kilometers

        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

        a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    shops = frappe.get_all("Shop", fields=["name", "latitude", "longitude", "is_ecommerce"])
    nearby_shops = []
    for shop in shops:
        if shop.is_ecommerce:
            nearby_shops.append(shop)
            continue

        if shop.latitude and shop.longitude:
            distance = haversine(latitude, longitude, shop.latitude, shop.longitude)
            if distance <= radius_km:
                nearby_shops.append(shop)

    return nearby_shops

@frappe.whitelist()
def get_shop_branch(shop_id: str, lang: str = "en"):
    """
    Retrieves the branches for a given shop.
    """
    return frappe.get_all("Branch", filters={"shop": shop_id})

@frappe.whitelist()
def join_order(shop_id: str, cart_id: str, lang: str = "en"):
    """
    Joins a group order.
    """
    user = frappe.session.user
    shop_cart = frappe.get_doc("Shop Cart", {"shop": shop_id, "cart": cart_id})
    shop_cart.append("users", {"user": user})
    shop_cart.save(ignore_permissions=True)
    return shop_cart.as_dict()

@frappe.whitelist()
def get_shop_filter(category_id: int = None, sub_category_id: int = None, page: int = 1, lang: str = "en"):
    """
    Retrieves a list of shops based on a filter.
    """
    filters = {"doctype": "Shop", "disabled": 0}
    if sub_category_id:
        filters["category"] = sub_category_id
    elif category_id:
        filters["category"] = category_id

    shops = frappe.get_list(
        "Shop",
        filters=filters,
        fields=["name", "shop_name", "logo"],
        limit_start=(page - 1) * 10,
        limit_page_length=10,
    )
    return shops

@frappe.whitelist()
def get_pickup_shops(lang: str = "en"):
    """
    Retrieves a list of shops that offer pickup.
    """
    shops = frappe.get_list(
        "Shop",
        filters={"delivery_type": "Pickup"},
        fields=["name", "shop_name", "logo"],
    )
    return shops

@frappe.whitelist()
def get_shops_by_ids(shop_ids: list, lang: str = "en"):
    """
    Retrieves a list of shops by their IDs.
    """
    shops = frappe.get_list(
        "Shop",
        filters={"name": ["in", shop_ids]},
        fields=["name", "shop_name", "logo"],
    )
    return shops

@frappe.whitelist()
def create_shop(shop_data: dict, lang: str = "en"):
    """
    Creates a new shop.
    """
    shop = frappe.get_doc({
        "doctype": "Shop",
        **shop_data
    })
    shop.insert(ignore_permissions=True)
    return shop.as_dict()

@frappe.whitelist()
def get_shops_recommend(page: int = 1, lang: str = "en"):
    """
    Retrieves a list of recommended shops.
    """
    shops = frappe.get_list(
        "Shop",
        filters={"recommended": 1},
        fields=["name", "shop_name", "logo"],
        limit_start=(page - 1) * 10,
        limit_page_length=10,
    )
    return shops

@frappe.whitelist()
def get_story(page: int = 1, lang: str = "en"):
    """
    Retrieves a list of stories grouped by shop for Flutter.
    """
    stories = frappe.get_list(
        "Story",
        fields=["name", "shop", "image", "title", "product", "creation", "modified"],
        limit_start=(page - 1) * 10,
        limit_page_length=10,
    )
    
    grouped = {}
    for s in stories:
        shop_id = s.shop
        if not shop_id: continue
        
        if shop_id not in grouped:
            grouped[shop_id] = []
        
        shop_logo = frappe.db.get_value("Shop", shop_id, "logo")
        
        grouped[shop_id].append({
            "shop_id": int(shop_id) if shop_id.isdigit() else shop_id,
            "logo_img": shop_logo,
            "title": s.title,
            "product_uuid": s.product,
            "product_title": frappe.db.get_value("Product", s.product, "product_name") if s.product else None,
            "url": s.image,
            "created_at": s.creation.isoformat() if s.creation else None,
            "updated_at": s.modified.isoformat() if s.modified else None,
        })
        
    return list(grouped.values())

@frappe.whitelist()
def get_tags(category_id: int, lang: str = "en"):
    """
    Retrieves a list of tags.
    """
    return frappe.get_all("Tag", fields=["name", "tag_name"])

@frappe.whitelist()
def get_suggest_price(lang: str = "en"):
    """
    Retrieves a suggested price range.
    """
    # Simply return a response that matches PriceModel.fromJson
    import datetime
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": True,
        "message": "Suggested price retrieved",
        "data": {
            "min": 10.0,
            "max": 1000.0
        }
    }

@frappe.whitelist()
def get_referral_details(lang: str = "en"):
    """
    Retrieves the referral details for the current user.
    """
    user = frappe.session.user
    if not frappe.db.exists("Referral", {"user": user}):
        # Create a new referral code if one doesn't exist
        from frappe.utils import random_string
        referral_code = random_string(10)
        referral = frappe.new_doc("Referral")
        referral.user = user
        referral.referral_code = referral_code
        referral.insert(ignore_permissions=True)
    else:
        referral = frappe.get_doc("Referral", {"user": user})
    return referral.as_dict()

@frappe.whitelist()
def set_active_address(address_id: str, lang: str = "en"):
    """
    Sets an address as the active address for the current user.
    """
    user = frappe.session.user
    # Set all other addresses for this user to inactive
    frappe.db.set_value("Address", {"user": user}, "is_active", 0)
    # Set the selected address to active
    frappe.db.set_value("Address", address_id, "is_active", 1)
    return {"status": "success"}

@frappe.whitelist()
def delete_account(lang: str = "en"):
    """
    Deletes the current user's account (soft delete).
    """
    user = frappe.session.user
    frappe.db.set_value("User", user, "enabled", 0)
    return {"status": "success"}

@frappe.whitelist()
def update_profile_image(image_url: str, lang: str = "en"):
    """
    Updates the profile image for the current user.
    """
    user = frappe.session.user
    frappe.db.set_value("User", user, "user_image", image_url)
    return frappe.get_doc("User", user).as_dict()

@frappe.whitelist()
def update_password(password: str, lang: str = "en"):
    """
    Updates the password for the current user.
    """
    user = frappe.session.user
    frappe.utils.password.update_password(user, password)
    return {"status": "success"}

@frappe.whitelist()
def search_user(name: str, page: int = 1, lang: str = "en"):
    """
    Searches for users by name.
    """
    users = frappe.get_list(
        "User",
        filters={"full_name": ["like", f"%{name}%"]},
        fields=["name", "full_name", "user_image"],
        limit_start=(page - 1) * 10,
        limit_page_length=10,
    )
    return users

@frappe.whitelist()
def get_product_calculations(stock_id: str, quantity: int, lang: str = "en"):
    """
    Calculates the price for a single product.
    """
    item = frappe.get_doc("Product", stock_id)
    total_price = item.price * quantity
    return {"total_price": total_price}

@frappe.whitelist()
def upload_multi_image(files: list, upload_type: str, doc_name: str = None, lang: str = "en"):
    """
    Uploads multiple images and attaches them to a document.
    """
    doctype = ""
    if upload_type == "extras":
        doctype = "Product Extra"
    elif upload_type == "brands":
        doctype = "Brand"
    elif upload_type == "categories":
        doctype = "Category"
    elif upload_type == "shopsLogo":
        doctype = "Shop"
    elif upload_type == "shopsBack":
        doctype = "Shop"
    elif upload_type == "products":
        doctype = "Product"
    elif upload_type == "reviews":
        doctype = "Review"
    elif upload_type == "users":
        doctype = "User"

    if not doctype:
        frappe.throw("Invalid upload type.")

    if not doc_name and doctype != "User":
        frappe.throw("doc_name is required for this upload type.")

    doc = frappe.get_doc(doctype, doc_name if doc_name else frappe.session.user)

    file_urls = []
    for file in files:
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file.filename,
            "attached_to_doctype": doctype,
            "attached_to_name": doc.name,
            "content": file.file.getvalue(),
            "is_private": 0,
        })
        file_doc.insert()
        file_urls.append(file_doc.file_url)

    if upload_type == "shopsLogo":
        doc.logo = file_urls[0]
    elif upload_type == "shopsBack":
        doc.background_image = file_urls[0]
    elif upload_type == "users":
        doc.user_image = file_urls[0]

    doc.save()

    return {"file_urls": file_urls}

@frappe.whitelist()
def process_token_payment(order_id: str, token: str, lang: str = "en"):
    """
    Processes a payment for an order using a token.
    """
    # This is a placeholder for the actual payment gateway integration.
    # In a real system, this would involve calling the payment gateway's API.
    frappe.db.set_value("Order", order_id, "status", "Paid")
    return {"status": "success"}

@frappe.whitelist()
def tip_process(order_id: str, tip: float, lang: str = "en"):
    """
    Processes a tip for an order.
    """
    tip = frappe.get_doc({
        "doctype": "Tip",
        "order": order_id,
        "tip": tip,
    })
    tip.insert(ignore_permissions=True)
    return tip.as_dict()

@frappe.whitelist()
def check_cashback(shop_id: str, amount: float, lang: str = "en"):
    """
    Checks the cashback for a given shop and amount based on defined rules.
    """
    cashback_rule = frappe.db.get_value(
        "Cashback Rule",
        filters={"shop": shop_id, "min_amount": ["<=", amount]},
        fieldname=["percentage"],
        order_by="min_amount desc",
    )

    if cashback_rule:
        cashback_amount = (amount * cashback_rule) / 100
        return {"cashback_amount": cashback_amount}

    return {"cashback_amount": 0}

@frappe.whitelist()
def get_driver_location(order_id: str, lang: str = "en"):
    """
    Retrieves the driver's location for a given order.
    """
    driver_location = frappe.get_list("Driver Location",
        filters={"order": order_id},
        fields=["latitude", "longitude"],
        order_by="creation desc",
        limit=1)

    if driver_location:
        return driver_location[0]

    return {}

@frappe.whitelist()
def create_transaction(order_id: str, payment_id: str, lang: str = "en"):
    """
    Creates a new transaction.
    """
    transaction = frappe.get_doc({
        "doctype": "Transaction",
        "order": order_id,
        "payment_gateway": payment_id,
    })
    transaction.insert(ignore_permissions=True)
    return transaction.as_dict()

@frappe.whitelist()
def get_notification_types():
    """
    Retrieves a list of all available notification types.
    """
    return frappe.get_all("Notification Type", fields=["type", "payload"])

@frappe.whitelist()
def get_user_notification_preferences():
    """
    Retrieves the notification preferences for the current user.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to view your notification preferences.")

    preferences = frappe.get_all(
        "User Notification Preference",
        filters={"user": user},
        fields=["notification_type", "active"]
    )
    return preferences

@frappe.whitelist()
def set_user_notification_preference(notification_type, active):
    """
    Sets the notification preference for the current user.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to set your notification preferences.")

    if not frappe.db.exists("Notification Type", {"type": notification_type}):
        frappe.throw("Invalid notification type.")

    preference = frappe.get_doc({
        "doctype": "User Notification Preference",
        "user": user,
        "notification_type": notification_type
    })
    preference.active = active
    preference.save(ignore_permissions=True)
    return preference.as_dict()

@frappe.whitelist()
def get_notification_logs(limit_start: int = 0, limit_page_length: int = 20):
    """
    Retrieves a list of notification logs for the current user.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to view your notification logs.")

    logs = frappe.get_list(
        "Notification Log",
        filters={"user": user},
        fields=["notification_type", "subject", "message", "read", "creation"],
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        order_by="creation desc"
    )
    return logs

@frappe.whitelist()
def mark_notification_logs_as_read(notification_log_ids):
    """
    Marks a list of notification logs as read.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to mark notifications as read.")

    if isinstance(notification_log_ids, str):
        notification_log_ids = json.loads(notification_log_ids)

    for log_id in notification_log_ids:
        log = frappe.get_doc("Notification Log", log_id)
        if log.user == user:
            log.read = 1
            log.save(ignore_permissions=True)

    return {"status": "success"}

@frappe.whitelist()
def get_global_settings(lang: str = "en"):
    """
    Retrieves the global settings.
    """
    return frappe.get_doc("Global Settings")

@frappe.whitelist()
def get_mobile_translations(lang: str = "en"):
    """
    Retrieves the mobile translations for the given language.
    """
    # This is a placeholder for the actual implementation.
    return {"translations": {}}

@frappe.whitelist()
def get_faqs(lang: str = "en"):
    """
    Retrieves a list of frequently asked questions.
    """
    return frappe.get_all("FAQ", fields=["name", "question", "answer"])

@frappe.whitelist()
def get_terms(lang: str = "en"):
    """
    Retrieves the terms of service.
    """
    # This is a placeholder for the actual implementation.
    return {"terms": "<h1>Terms of Service</h1>"}

@frappe.whitelist()
def get_policy(lang: str = "en"):
    """
    Retrieves the privacy policy.
    """
    # This is a placeholder for the actual implementation.
    return {"policy": "<h1>Privacy Policy</h1>"}

@frappe.whitelist()
def update_notification_status(notification_ids: list, lang: str = "en"):
    """
    Updates the status of a list of notifications.
    """
    for notification_id in notification_ids:
        frappe.db.set_value("Notification Log", notification_id, "read", 1)
    return {"status": "success"}

@frappe.whitelist()
def search_users(search: str, lang: str = "en"):
    """
    Searches for users by name or email.
    """
    users = frappe.get_list(
        "User",
        filters=[
            ["User", "full_name", "like", f"%{search}%"],
            ["User", "email", "like", f"%{search}%"]
        ],
        fields=["name", "full_name", "user_image"],
        or_filters=True,
    )
    return users

@frappe.whitelist()
def send_wallet_balance(receiver: str, amount: float, lang: str = "en"):
    """
    Sends wallet balance from the current user to another user.
    """
    sender = frappe.session.user

    # This is a placeholder for the actual wallet logic.
    # In a real system, this would involve creating a transaction,
    # updating wallet balances, and handling potential errors.

    return {
        "status": "success",
        "message": "Wallet balance sent successfully.",
        "data": {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
        }
    }

@frappe.whitelist()
def forgot_password_confirm(verify_code: str, email: str, lang: str = "en"):
    """
    Confirms a password reset.
    """
    password_reset = frappe.get_doc("Password Reset", {"token": verify_code, "user": email})
    if password_reset.used:
        frappe.throw("This password reset link has already been used.")

    password_reset.used = 1
    password_reset.save(ignore_permissions=True)

    return {"status": "success"}

@frappe.whitelist()
def forgot_password_confirm_with_phone(phone: str, lang: str = "en"):
    """
    Confirms a password reset with a phone number.
    """
    # This is a placeholder for the actual implementation.
    # In a real system, this would involve sending a code to the user's phone.
    return {"status": "success"}

@frappe.whitelist()
def get_banners(page: int = 1, limit_page_length: int = 10, lang: str = "en"):
    """
    Retrieves a list of banners.
    """
    banners = frappe.get_list(
        "Banner",
        fields=["name", "title", "image", "url"],
        limit_start=(page - 1) * limit_page_length,
        limit_page_length=limit_page_length,
    )
    return banners

@frappe.whitelist()
def get_ads(page: int = 1, limit_page_length: int = 10, lang: str = "en"):
    """
    Retrieves a list of ads.
    """
    ads = frappe.get_list(
        "Ad",
        fields=["name", "title", "image", "url"],
        limit_start=(page - 1) * limit_page_length,
        limit_page_length=limit_page_length,
    )
    return ads

@frappe.whitelist()
def get_banner(id: int, lang: str = "en"):
    """
    Retrieves a single banner.
    """
    return frappe.get_doc("Banner", id)

@frappe.whitelist()
def get_ad(id: int, lang: str = "en"):
    """
    Retrieves a single ad.
    """
    return frappe.get_doc("Ad", id)

@frappe.whitelist()
def like_banner(id: int, lang: str = "en"):
    """
    Likes a banner.
    """
    banner = frappe.get_doc("Banner", id)
    banner.likes += 1
    banner.save(ignore_permissions=True)
    return {"status": "success"}

@frappe.whitelist(allow_guest=True)
def login_with_google(email: str, display_name: str, id: str, avatar: str, lang: str = "en"):
    """
    Logs in a user with their Google account.
    """
    if frappe.db.exists("Google User", {"google_user_id": id}):
        google_user = frappe.get_doc("Google User", {"google_user_id": id})
        user = frappe.get_doc("User", google_user.user)
    elif frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
        google_user = frappe.new_doc("Google User")
        google_user.user = user.name
        google_user.google_user_id = id
        google_user.insert(ignore_permissions=True)
    else:
        user = frappe.new_doc("User")
        user.email = email
        user.first_name = display_name
        user.send_welcome_email = 0
        user.insert(ignore_permissions=True)
        google_user = frappe.new_doc("Google User")
        google_user.user = user.name
        google_user.google_user_id = id
        google_user.insert(ignore_permissions=True)

    frappe.local.login_manager.login_as(user.name)

    return frappe.local.response

@frappe.whitelist(allow_guest=True)
def sig_up(email: str, lang: str = "en"):
    """
    Placeholder for email-based signup.
    """
    return {"status": "success"}

@frappe.whitelist(allow_guest=True)
def sig_up_with_phone(user: dict, lang: str = "en"):
    """
    Placeholder for phone-based signup.
    """
    return {"status": "success"}

@frappe.whitelist()
def get_banners(page: int = 1, limit_page_length: int = 10, lang: str = "en"):
    """
    Retrieves a list of banners.
    """
    banners = frappe.get_list(
        "Banner",
        fields=["name", "title", "image", "url"],
        limit_start=(page - 1) * limit_page_length,
        limit_page_length=limit_page_length,
    )
    return banners

@frappe.whitelist()
def get_ads(page: int = 1, limit_page_length: int = 10, lang: str = "en"):
    """
    Retrieves a list of ads.
    """
    ads = frappe.get_list(
        "Ad",
        fields=["name", "title", "image", "url"],
        limit_start=(page - 1) * limit_page_length,
        limit_page_length=limit_page_length,
    )
    return ads

@frappe.whitelist()
def get_banner(id: int, lang: str = "en"):
    """
    Retrieves a single banner.
    """
    return frappe.get_doc("Banner", id)

@frappe.whitelist()
def get_ad(id: int, lang: str = "en"):
    """
    Retrieves a single ad.
    """
    return frappe.get_doc("Ad", id)

@frappe.whitelist()
def like_banner(id: int, lang: str = "en"):
    """
    Likes a banner.
    """
    banner = frappe.get_doc("Banner", id)
    banner.likes += 1
    banner.save(ignore_permissions=True)
    return {"status": "success"}

@frappe.whitelist()
def create_cart(cart: dict, lang: str = "en"):
    """
    Creates a new cart.
    """
    cart_doc = frappe.get_doc({
        "doctype": "Cart",
        "user": frappe.session.user,
        "shop": cart.get("shop_id"),
    })
    for item in cart.get("items", []):
        cart_doc.append("items", {
            "item": item.get("item_code"),
            "quantity": item.get("quantity"),
        })
    cart_doc.insert(ignore_permissions=True)
    return cart_doc.as_dict()

@frappe.whitelist()
def insert_cart(cart: dict, lang: str = "en"):
    """
    Inserts items into an existing cart.
    """
    cart_doc = frappe.get_doc("Cart", cart.get("cart_id"))
    for item in cart.get("items", []):
        cart_doc.append("items", {
            "item": item.get("item_code"),
            "quantity": item.get("quantity"),
        })
    cart_doc.save(ignore_permissions=True)
    return cart_doc.as_dict()

@frappe.whitelist()
def insert_cart_with_group(cart: dict, lang: str = "en"):
    """
    Inserts items into an existing group cart.
    """
    cart_doc = frappe.get_doc("Cart", cart.get("cart_id"))
    for item in cart.get("items", []):
        cart_doc.append("items", {
            "item": item.get("item_code"),
            "quantity": item.get("quantity"),
        })
    cart_doc.save(ignore_permissions=True)
    return cart_doc.as_dict()

@frappe.whitelist()
def create_and_cart(cart: dict, lang: str = "en"):
    """
    Creates a new cart and adds items to it.
    """
    return create_cart(cart, lang)

@frappe.whitelist()
def get_cart_in_group(cart_id: str, shop_id: str, cart_uuid: str, lang: str = "en"):
    """
    Retrieves a group cart.
    """
    return frappe.get_doc("Cart", cart_id)

@frappe.whitelist()
def delete_cart(cart_id: int, lang: str = "en"):
    """
    Deletes a cart.
    """
    frappe.delete_doc("Cart", cart_id, ignore_permissions=True)
    return {"status": "success"}

@frappe.whitelist()
def change_status(user_uuid: str, cart_id: str, lang: str = "en"):
    """
    Changes the status of a user in a group cart.
    """
    # This is a placeholder for the actual implementation.
    return {"status": "success"}

@frappe.whitelist()
def delete_user(cart_id: int, user_id: str, lang: str = "en"):
    """
    Deletes a user from a group cart.
    """
    cart_doc = frappe.get_doc("Cart", cart_id)
    cart_doc.remove("group_order_users", {"user": user_id})
    cart_doc.save(ignore_permissions=True)
    return cart_doc.as_dict()

@frappe.whitelist()
def start_group_order(cart_id: int, lang: str = "en"):
    """
    Starts a group order.
    """
    cart_doc = frappe.get_doc("Cart", cart_id)
    cart_doc.is_group_order = 1
    cart_doc.save(ignore_permissions=True)
    return cart_doc.as_dict()

@frappe.whitelist()
def remove_product_cart(cart_detail_id: int, list_of_id: list = None, lang: str = "en"):
    """
    Removes a product from a cart.
    """
    frappe.delete_doc("Cart Detail", cart_detail_id, ignore_permissions=True)
    return {"status": "success"}

@frappe.whitelist()
def check_loan_eligibility(id_number: str, amount: float, lang: str = "en"):
    """
    Checks if a user is eligible for a loan.
    """
    # This is a placeholder for the actual scorecard logic.
    is_eligible = True
    loan_eligibility_check = frappe.get_doc({
        "doctype": "Loan Eligibility Check",
        "id_number": id_number,
        "amount": amount,
        "is_eligible": is_eligible,
    })
    loan_eligibility_check.insert(ignore_permissions=True)
    return {"is_eligible": is_eligible}

@frappe.whitelist()
def check_loan_history_eligibility(lang: str = "en"):
    """
    Checks if a user is eligible for a loan based on their loan history.
    """
    # This is a placeholder for the actual scorecard logic.
    return {"has_disqualifying_history": False}

@frappe.whitelist()
def mark_application_as_rejected(financial_details: dict, lang: str = "en"):
    """
    Marks a loan application as rejected.
    """
    # This is a placeholder for the actual scorecard logic.
    return {"status": "success"}

@frappe.whitelist()
def check_financial_eligibility(monthly_income: float, grocery_expenses: float, other_expenses: float, existing_credits: float, lang: str = "en"):
    """
    Checks if a user is financially eligible for a loan.
    """
    # This is a placeholder for the actual scorecard logic.
    return {"is_eligible": True}

@frappe.whitelist()
def save_incomplete_loan_application(financial_details: dict, lang: str = "en"):
    """
    Saves an incomplete loan application as a draft.
    """
    loan_application = frappe.get_doc({
        "doctype": "Loan Application",
        "status": "Draft",
        # ... save other details from financial_details ...
    })
    loan_application.insert(ignore_permissions=True)
    return {"name": loan_application.name}

@frappe.whitelist()
def fetch_saved_application(lang: str = "en"):
    """
    Fetches a saved loan application.
    """
    user = frappe.session.user
    loan_application = frappe.get_list(
        "Loan Application",
        filters={"customer": user, "status": "Draft"},
        limit=1,
    )
    if loan_application:
        return frappe.get_doc("Loan Application", loan_application[0].name)
    return {}

@frappe.whitelist()
def fetch_saved_applications(lang: str = "en"):
    """
    Fetches all saved loan applications for the current user.
    """
    user = frappe.session.user
    loan_applications = frappe.get_list(
        "Loan Application",
        filters={"customer": user, "status": "Draft"},
    )
    return loan_applications

@frappe.whitelist()
def read_all_notifications(lang: str = "en"):
    """
    Marks all notifications for the current user as read.
    """
    user = frappe.session.user
    frappe.db.set_value("Notification Log", {"for_user": user}, "read", 1)
    return {"status": "success"}

@frappe.whitelist()
def read_one_notification(notification_id: int, lang: str = "en"):
    """
    Marks a single notification as read.
    """
    frappe.db.set_value("Notification Log", notification_id, "read", 1)
    return {"status": "success"}

@frappe.whitelist()
def get_notification_count(lang: str = "en"):
    """
    Retrieves the number of unread notifications for the current user.
    """
    user = frappe.session.user
    count = frappe.db.count("Notification Log", {"for_user": user, "read": 0})
    return {"count": count}

@frappe.whitelist()
def add_parcel_review(order_id: str, rating: float, comment: str, lang: str = "en"):
    """
    Adds a review for a parcel order.
    """
    parcel_review = frappe.get_doc({
        "doctype": "Parcel Review",
        "order": order_id,
        "rating": rating,
        "comment": comment,
    })
    parcel_review.insert(ignore_permissions=True)
    return parcel_review.as_dict()

@frappe.whitelist()
def get_parcel_categories(lang: str = "en"):
    """
    Retrieves a list of parcel categories.
    """
    return frappe.get_all("Parcel Category", fields=["name", "category_name"])

@frappe.whitelist()
def get_parcel_calculate(category_id: str, distance_km: float, lang: str = "en"):
    """
    Calculates the price for a parcel delivery.
    """
    # This is a placeholder for the actual calculation logic.
    return {"price": distance_km * 1.5}

@frappe.whitelist()
def initiate_parcel_payment(order_id: int, payment_gateway: str, lang: str = "en"):
    """
    Initiates a payment for a parcel order.
    """
    # This is a placeholder for the actual payment gateway integration.
    return {"redirect_url": "https://example.com/payment"}

@frappe.whitelist()
def create_parcel_transaction(order_id: int, payment_id: int, lang: str = "en"):
    """
    Creates a new transaction for a parcel order.
    """
    transaction = frappe.get_doc({
        "doctype": "Transaction",
        "order": order_id,
        "payment_gateway": payment_id,
    })
    transaction.insert(ignore_permissions=True)
    return transaction.as_dict()
