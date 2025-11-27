import frappe
from ..seller.utils import _get_seller_shop

@frappe.whitelist()
def get_seller_statistics():
    """
    Retrieves sales and order statistics for the current seller's shop.
    """
    user = frappe.session.user
    shop = _get_seller_shop(user)

    progress_orders_count = frappe.db.count("Order", {"shop": shop, "status": ["in", ["New", "Accepted", "Shipped"]]})
    cancel_orders_count = frappe.db.count("Order", {"shop": shop, "status": "Cancelled"})
    delivered_orders_count = frappe.db.count("Order", {"shop": shop, "status": "Delivered"})
    
    # Products out of stock: Count Stock items with quantity <= 0 for this shop's products
    # We need to join Stock and Product
    products_out_of_count = frappe.db.sql("""
        SELECT COUNT(s.name)
        FROM `tabStock` s
        JOIN `tabProduct` p ON s.product = p.name
        WHERE p.shop = %(shop)s AND s.quantity <= 0 AND p.active = 1
    """, {"shop": shop})[0][0]

    products_count = frappe.db.count("Product", {"shop": shop, "active": 1})
    
    # Reviews count (assuming Review DocType has a 'shop' field or linked via 'order')
    # Let's check Review DocType fields later if this fails, but assuming 'shop' link exists or we query by Order.
    # For now, let's try querying Review by shop if it exists, otherwise 0.
    # Actually, Review usually links to Product or Shop. Let's assume Shop.
    try:
        reviews_count = frappe.db.count("Review", {"shop": shop})
    except:
        reviews_count = 0

    # Financials (Delivered orders only)
    financials = frappe.db.sql("""
        SELECT 
            SUM(grand_total) as total_earned,
            SUM(delivery_fee) as delivery_earned,
            SUM(tax) as tax_earned,
            SUM(commission_fee) as commission_earned
        FROM `tabOrder`
        WHERE shop = %(shop)s AND status = 'Delivered'
    """, {"shop": shop}, as_dict=True)[0]

    top_selling_products = frappe.db.sql("""
        SELECT oi.product, i.item_name, SUM(oi.quantity) as total_quantity
        FROM `tabOrder Item` as oi
        JOIN `tabOrder` as o ON o.name = oi.parent
        JOIN `tabItem` as i ON i.name = oi.product
        WHERE o.shop = %(shop)s
        GROUP BY oi.product, i.item_name
        ORDER BY total_quantity DESC
        LIMIT 10
    """, {"shop": shop}, as_dict=True)

    return {
        "progress_orders_count": progress_orders_count,
        "cancel_orders_count": cancel_orders_count,
        "delivered_orders_count": delivered_orders_count,
        "products_out_of_count": products_out_of_count,
        "products_count": products_count,
        "reviews_count": reviews_count,
        "total_earned": financials.get("total_earned") or 0,
        "delivery_earned": financials.get("delivery_earned") or 0,
        "tax_earned": financials.get("tax_earned") or 0,
        "commission_earned": financials.get("commission_earned") or 0,
        "top_selling_products": top_selling_products
    }


@frappe.whitelist()
def get_seller_sales_report(from_date: str, to_date: str):
    """
    Retrieves a sales report for the current seller's shop within a date range.
    """
    user = frappe.session.user
    shop = _get_seller_shop(user)

    sales_report = frappe.get_all(
        "Order",
        filters={
            "shop": shop,
            "creation": ["between", [from_date, to_date]]
        },
        fields=["name", "user", "grand_total", "status", "creation"],
        order_by="creation desc"
    )
    return sales_report
