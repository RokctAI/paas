import frappe
import json
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)
def create_order(order_data):
    """
    Creates a new order.
    """
    if isinstance(order_data, str):
        order_data = json.loads(order_data)

    # Check for hierarchical auto-approval
    paas_settings = frappe.get_single("Permission Settings")

    # Validate phone number if required by admin settings
    if paas_settings.require_phone_for_order and not order_data.get("phone"):
        frappe.throw("A phone number is required to create this order.", frappe.ValidationError)

    shop = frappe.get_doc("Shop", order_data.get("shop"))

    initial_status = "New"
    if paas_settings.auto_approve_orders and shop.auto_approve_orders:
        initial_status = "Accepted"

    order = frappe.get_doc({
        "doctype": "Order",
        "user": order_data.get("user"),
        "shop": order_data.get("shop"),
        "status": initial_status,
        "delivery_type": order_data.get("delivery_type"),
        "currency": order_data.get("currency"),
        "rate": order_data.get("rate"),
        "delivery_fee": order_data.get("delivery_fee"),
        "waiter_fee": order_data.get("waiter_fee"),
        "tax": order_data.get("tax"),
        "commission_fee": order_data.get("commission_fee"),
        "service_fee": order_data.get("service_fee"),
        "total_discount": order_data.get("total_discount"),
        "coupon_code": order_data.get("coupon_code"),
        "location": order_data.get("location"),
        "address": order_data.get("address"),
        "phone": order_data.get("phone"),
        "username": order_data.get("username"),
        "delivery_date": order_data.get("delivery_date"),
        "delivery_time": order_data.get("delivery_time"),
        "note": order_data.get("note"),
    })

    # Calculate cashback
    cashback_amount = frappe.call("paas.api.check_cashback", shop_id=order_data.get("shop"), amount=order.grand_total)
    order.cashback_amount = cashback_amount.get("cashback_amount")

    for item in order_data.get("order_items", []):
        order.append("order_items", {
            "product": item.get("product"),
            "quantity": item.get("quantity"),
            "price": item.get("price"),
        })

    order.insert(ignore_permissions=True)

    if order_data.get("coupon_code"):
        coupon = frappe.get_doc("Coupon", {"code": order_data.get("coupon_code")})
        frappe.get_doc({
            "doctype": "Coupon Usage",
            "coupon": coupon.name,
            "user": order.user,
            "order": order.name
        }).insert(ignore_permissions=True)

    return order.as_dict()


@frappe.whitelist()
def list_orders(limit_start: int = 0, limit_page_length: int = 20):
    """
    Retrieves a list of orders for the current user.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to view your orders.")

    orders = frappe.get_list(
        "Order",
        filters={"user": user},
        fields=["name", "shop", "total_price", "status", "creation"],
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        order_by="creation desc"
    )
    return orders


@frappe.whitelist()
def get_order_details(order_id: str):
    """
    Retrieves the details of a specific order.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to view your orders.")

    order = frappe.get_doc("Order", order_id)
    if order.user != user:
        frappe.throw("You are not authorized to view this order.", frappe.PermissionError)
    return order.as_dict()


@frappe.whitelist()
def update_order_status(order_id: str, status: str):
    """
    Updates the status of a specific order.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to update an order.")

    order = frappe.get_doc("Order", order_id)

    if order.user != user and "System Manager" not in frappe.get_roles(user):
        frappe.throw("You are not authorized to update this order.", frappe.PermissionError)

    valid_statuses = frappe.get_meta("Order").get_field("status").options.split("\n")
    if status not in valid_statuses:
        frappe.throw(f"Invalid status. Must be one of {', '.join(valid_statuses)}")

    order.status = status
    order.save(ignore_permissions=True)
    return order.as_dict()


@frappe.whitelist()
def add_order_review(order_id: str, rating: float, comment: str = None):
    """
    Adds a review for a specific order.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to leave a review.")

    order = frappe.get_doc("Order", order_id)

    if order.user != user:
        frappe.throw("You can only review your own orders.", frappe.PermissionError)

    if order.status != "Delivered":
        frappe.throw("You can only review delivered orders.")

    if frappe.db.exists("Review", {"reviewable_type": "Order", "reviewable_id": order_id, "user": user}):
        frappe.throw("You have already reviewed this order.")

    review = frappe.get_doc({
        "doctype": "Review",
        "reviewable_type": "Order",
        "reviewable_id": order_id,
        "user": user,
        "rating": rating,
        "comment": comment,
        "published": 1
    })
    review.insert(ignore_permissions=True)
    return review.as_dict()


@frappe.whitelist()
def cancel_order(order_id: str):
    """
    Cancels a specific order.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to cancel an order.")

    order = frappe.get_doc("Order", order_id)

    if order.user != user and "System Manager" not in frappe.get_roles(user):
        frappe.throw("You are not authorized to cancel this order.", frappe.PermissionError)

    if order.status != "New":
        frappe.throw("You can only cancel orders that have not been accepted yet.")

    order.status = "Cancelled"

    # Replenish stock by creating a Stock Entry for stock reconciliation
    stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "purpose": "Stock Reconciliation",
        "items": []
    })
    for item in order.order_items:
        stock_entry.append("items", {
            "item_code": item.product,
            "qty": item.quantity,
            "s_warehouse": "Stores", # Or get from product/order
            "t_warehouse": "Stores", # Or get from product/order
            "diff_qty": item.quantity,
            "basic_rate": item.price
        })
    stock_entry.insert(ignore_permissions=True)
    stock_entry.submit()

    order.save(ignore_permissions=True)
    return order.as_dict()

@frappe.whitelist(allow_guest=True)
def get_order_statuses():
    """
    Retrieves a list of active order statuses, formatted for frontend compatibility.
    """
    statuses = frappe.get_list(
        "Order Status",
        filters={"is_active": 1},
        fields=["name", "status_name", "sort_order"],
        order_by="sort_order asc"
    )

    formatted_statuses = []
    for status in statuses:
        formatted_statuses.append({
            "id": status.name,
            "name": status.status_name,
            "active": True,
            "sort": status.sort_order,
        })

    return formatted_statuses


@frappe.whitelist()
def get_calculate(cart_id, address=None, coupon_code=None, tips=0, delivery_type='Delivery'):
    if isinstance(address, str):
        address = json.loads(address)

    cart = frappe.get_doc("Cart", cart_id)
    shop = frappe.get_doc("Shop", cart.shop)

    # 1. Calculate Product Totals
    price = 0
    total_tax = 0
    discount = 0
    for item in cart.items:
        item_doc = frappe.get_doc("Item", item.item_code)
        price += item_doc.standard_rate * item.qty
        # Assuming a 'tax' field on the Item doc
        if item_doc.tax:
            total_tax += item_doc.tax * item.qty
        # Discount logic might be more complex, this is a simplification
        if item.discount_percentage:
            discount += (item_doc.standard_rate * item.qty) * (item.discount_percentage / 100)

    # 2. Calculate Delivery Fee
    delivery_fee = 0
    if delivery_type == 'Delivery' and address:
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

        if shop.latitude and shop.longitude:
            distance = haversine(shop.latitude, shop.longitude, address['latitude'], address['longitude'])
            delivery_fee = distance * shop.price_per_km if shop.price_per_km else 0

    # 3. Calculate Shop Tax
    shop_tax = (price - discount) * (shop.tax / 100) if shop.tax else 0

    # 4. Get Service Fee from Permission Settings
    paas_settings = frappe.get_single("Permission Settings")
    service_fee = paas_settings.service_fee or 0

    # 5. Apply Coupon
    coupon_price = 0
    if coupon_code:
        try:
            coupon_doc = frappe.get_doc("Coupon", {"coupon_code": coupon_code, "shop": cart.shop})
            if coupon_doc:
                # Basic coupon logic, can be expanded
                if coupon_doc.coupon_type == 'Percentage':
                    coupon_price = (price - discount) * (coupon_doc.discount_percentage / 100)
                else: # Fixed Amount
                    coupon_price = coupon_doc.discount_amount
        except frappe.DoesNotExistError:
            pass # Coupon not found, so no discount applied

    # 6. Calculate Final Total
    total_price = (price - discount) + delivery_fee + shop_tax + service_fee - coupon_price + float(tips)

    return {
        'total_tax': total_tax,
        'price': price,
        'total_shop_tax': shop_tax,
        'total_price': max(total_price, 0),
        'total_discount': discount + coupon_price,
        'delivery_fee': delivery_fee,
        'service_fee': service_fee,
        'tips': tips,
        'coupon_price': coupon_price,
    }
