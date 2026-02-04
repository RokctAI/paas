import frappe
import json
from ..utils import _require_admin

@frappe.whitelist()
def get_admin_statistics():
    """
    Retrieves detailed statistics for the admin dashboard including cards and charts.
    """
    _require_admin()

    # Cards
    total_users = frappe.db.count("User")
    total_shops = frappe.db.count("Company")
    total_orders = frappe.db.count("Order")
    total_sales = frappe.db.sql("SELECT SUM(grand_total) FROM `tabOrder` WHERE status = 'Delivered'")[0][0] or 0
    
    in_progress_orders = frappe.db.count("Order", {"status": ["in", ["Pending", "Processing", "Ready", "On the way"]]})
    cancelled_orders = frappe.db.count("Order", {"status": "Cancelled"})
    delivered_orders = frappe.db.count("Order", {"status": "Delivered"})
    total_products = frappe.db.count("Product")
    total_reviews = frappe.db.count("Review")

    # Charts Data (Last 30 Days)
    from frappe.utils import add_days, getdate, nowdate
    
    # Orders per Day
    orders_chart = frappe.db.sql("""
        SELECT DATE(creation) as date, COUNT(*) as count 
        FROM `tabOrder` 
        WHERE creation > %s 
        GROUP BY DATE(creation) 
        ORDER BY DATE(creation) ASC
    """, (add_days(nowdate(), -30),), as_dict=True)

    # New Users per Day
    users_chart = frappe.db.sql("""
        SELECT DATE(creation) as date, COUNT(*) as count 
        FROM `tabUser` 
        WHERE creation > %s 
        GROUP BY DATE(creation) 
        ORDER BY DATE(creation) ASC
    """, (add_days(nowdate(), -30),), as_dict=True)

    # New Shops per Day
    shops_chart = frappe.db.sql("""
        SELECT DATE(creation) as date, COUNT(*) as count 
        FROM `tabCompany` 
        WHERE creation > %s 
        GROUP BY DATE(creation) 
        ORDER BY DATE(creation) ASC
    """, (add_days(nowdate(), -30),), as_dict=True)

    # Order Status Breakdown
    status_chart = frappe.db.sql("""
        SELECT status, COUNT(*) as count 
        FROM `tabOrder` 
        GROUP BY status
    """, as_dict=True)

    return {
        "cards": {
            "total_users": total_users,
            "total_shops": total_shops,
            "total_orders": total_orders,
            "total_sales": total_sales,
            "in_progress_orders": in_progress_orders,
            "cancelled_orders": cancelled_orders,
            "delivered_orders": delivered_orders,
            "total_products": total_products,
            "total_reviews": total_reviews
        },
        "charts": {
            "orders_per_day": orders_chart,
            "new_users": users_chart,
            "new_shops": shops_chart,
            "order_status": status_chart
        }
    }

@frappe.whitelist()
def get_multi_company_sales_report(from_date: str, to_date: str, company: str = None):
    """
    Retrieves a sales report for a specific company or all companies within a date range (for admins).
    """
    _require_admin()

    filters = {
        "creation": ["between", [from_date, to_date]]
    }
    if company:
        filters["shop"] = company

    sales_report = frappe.get_all(
        "Order",
        filters=filters,
        fields=["name", "shop", "user", "grand_total", "status", "creation"],
        order_by="creation desc"
    )

    # Get commission rates for all shops
    commission_rates = frappe.get_all(
        "Company",
        fields=["name", "sales_commission_rate"],
        filters={"sales_commission_rate": [">", 0]}
    )
    commission_map = {c['name']: c['sales_commission_rate'] for c in commission_rates}

    for order in sales_report:
        commission_rate = commission_map.get(order.shop, 0)
        order.commission = (order.grand_total * commission_rate) / 100

    return sales_report

@frappe.whitelist()
def get_admin_report(doctype: str, fields: str, filters: str = None, limit_start: int = 0, limit_page_length: int = 20):
    """
    Retrieves a report for a specified doctype with given fields and filters (for admins).
    """
    _require_admin()

    if isinstance(fields, str):
        fields = json.loads(fields)

    if filters and isinstance(filters, str):
        filters = json.loads(filters)

    return frappe.get_list(
        doctype,
        fields=fields,
        filters=filters,
        limit_start=limit_start,
        limit_page_length=limit_page_length
    )

@frappe.whitelist()
def get_all_wallet_histories(limit_start: int = 0, limit_page_length: int = 20):
    """
    Retrieves a list of all wallet histories on the platform (for admins).
    """
    _require_admin()
    return frappe.get_list(
        "Wallet History",
        fields=["name", "wallet", "type", "price", "status", "created_at"],
        offset=limit_start,
        limit=limit_page_length,
        order_by="creation desc"
    )


@frappe.whitelist()
def get_all_transactions(limit_start: int = 0, limit_page_length: int = 20):
    """
    Retrieves a list of all transactions on the platform (for admins).
    """
    _require_admin()
    return frappe.get_list(
        "Transaction",
        fields=["name", "transaction_date", "reference_doctype", "reference_name", "debit", "credit", "currency"],
        offset=limit_start,
        limit=limit_page_length,
        order_by="creation desc"
    )


@frappe.whitelist()
def get_all_seller_payouts(limit_start: int = 0, limit_page_length: int = 20):
    """
    Retrieves a list of all seller payouts on the platform (for admins).
    """
    _require_admin()
    return frappe.get_list(
        "Seller Payout",
        fields=["name", "shop", "amount", "payout_date", "status"],
        offset=limit_start,
        limit=limit_page_length,
        order_by="payout_date desc"
    )


@frappe.whitelist()
def get_all_shop_bonuses(limit_start: int = 0, limit_page_length: int = 20):
    """
    Retrieves a list of all shop bonuses on the platform (for admins).
    """
    _require_admin()
    return frappe.get_list(
        "Shop Bonus",
        fields=["name", "shop", "amount", "bonus_date", "reason"],
        offset=limit_start,
        limit=limit_page_length,
        order_by="bonus_date desc"
    )
