import frappe

@frappe.whitelist()
def get_cart(shop_id: str):
    """
    Retrieves the active cart for the current user and a given shop.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to view your cart.")

    cart_name = frappe.db.get_value("Cart", {"owner": user, "shop": shop_id, "status": "Active"}, "name")
    if not cart_name:
        return None  # No active cart

    return frappe.get_doc("Cart", cart_name).as_dict()


@frappe.whitelist()
def add_to_cart(item_code: str, qty: int, shop_id: str):
    """
    Adds an item to the user's cart for a specific shop.
    Creates the cart if it doesn't exist.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to add items to your cart.")

    if not frappe.db.exists("Item", item_code):
        frappe.throw("Item not found.")

    item = frappe.get_doc("Item", item_code)
    price = item.standard_rate

    # Find or create the Cart document
    cart_name = frappe.db.get_value("Cart", {"owner": user, "shop": shop_id, "status": "Active"}, "name")
    if not cart_name:
        cart = frappe.get_doc({
            "doctype": "Cart",
            "owner": user,
            "shop": shop_id,
            "status": "Active"
        }).insert(ignore_permissions=True)
    else:
        cart = frappe.get_doc("Cart", cart_name)

    # Check if item already exists in cart
    existing_item = None
    for detail in cart.items:
        if detail.item == item_code:
            existing_item = detail
            break

    if existing_item:
        existing_item.quantity += qty
    else:
        cart.append("items", {
            "item": item_code,
            "quantity": qty,
            "price": price,
        })

    cart.save(ignore_permissions=True)

    # Recalculate totals
    calculate_cart_totals(cart.name)

    return cart.as_dict()


@frappe.whitelist()
def remove_from_cart(cart_detail_name: str):
    """
    Removes an item from the cart.
    `cart_detail_name` is the name of the Cart Detail row.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to modify your cart.")

    cart_detail = frappe.get_doc("Cart Detail", cart_detail_name)
    cart = frappe.get_doc("Cart", cart_detail.parent)

    if cart.owner != user:
        frappe.throw("You are not authorized to remove this item.", frappe.PermissionError)

    # Remove the item
    cart.remove(cart_detail)
    cart.save(ignore_permissions=True)

    # Recalculate totals
    calculate_cart_totals(cart.name)
    return {"status": "success", "message": "Item removed from cart."}


def calculate_cart_totals(cart_name: str):
    """
    Helper function to recalculate the total price of a cart.
    """
    cart = frappe.get_doc("Cart", cart_name)
    total_price = 0
    for detail in cart.items:
        total_price += detail.price * detail.quantity

    cart.total_price = total_price
    cart.save(ignore_permissions=True)
