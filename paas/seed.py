# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt
import frappe
import os
import re
import json
from frappe.utils import get_site_path, get_bench_path, getdate, now
from datetime import datetime

class LegacyDataSeeder:
    def __init__(self, site_name, db_path):
        self.site_name = site_name
        self.db_path = db_path
        self.user_id_map = {}
        self.shop_id_map = {}
        self.brand_id_map = {}
        self.category_id_map = {}
        self.unit_id_map = {}
        self.product_id_map = {}
        self.stock_id_map = {}
        self.orders_map = {}
        self.addresses_to_insert = []
        self.user_address_map = {}
        self.shop_section_map = {}
        self.table_map = {}
        self.parcel_setting_map = {}
        self.parcel_option_map = {}
        self.order_doc_map = {}
        self.banner_shop_map = {} # banner_id -> [shop_ids]
        self.wallet_uuid_map = {} # uuid -> doc_name
        self.transaction_id_map = {} # id -> doc_name
        self.payment_gateway_map = {
            '1': 'Cash', '2': 'Wallet', '3': 'PayPal', '4': 'Stripe',
            '5': 'Paystack', '6': 'PayFast', '7': 'Mpesa', '8': 'Braintree'
        }
        self.subscription_plan_map = {}

    def _safe_split(self, values_str):
        values = []
        in_quote = False
        current_val = ''
        i = 0
        while i < len(values_str):
            char = values_str[i]
            if char == "'":
                in_quote = not in_quote
                current_val += char
            elif char == ',' and not in_quote:
                values.append(current_val)
                current_val = ''
            else:
                current_val += char
            i += 1
        values.append(current_val)
        return [self._clean_value(v) for v in values]

    def _clean_value(self, value):
        if value is None:
            return None
        value = value.strip()
        if value == 'NULL':
            return None
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        return value

    def _map_user_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `users` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, name, email = parts[0], self._clean_value(parts[1]), self._clean_value(parts[2])
                    phone = self._clean_value(parts[4])

                    if not email: continue

                    if frappe.db.exists("User", email):
                        self.user_id_map[old_id] = email
                        continue

                    first_name = name.split(' ')[0] if name else f"User_{old_id}"
                    last_name = ' '.join(name.split(' ')[1:]) if name and ' ' in name else 'User'

                    frappe.get_doc({
                        "doctype": "User", "email": email, "first_name": first_name, "last_name": last_name,
                        "phone": phone, "send_welcome_email": 0, "roles": [{"role": "PaaS User"}]
                    }).insert(ignore_permissions=True)
                    self.user_id_map[old_id] = email
                    print(f"Inserted User: {email}")
                except Exception as e: print(f"Error user: {e}")

    def _map_shop_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `shops` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, name = parts[0], self._clean_value(parts[10])
                    if not name: continue

                    shop_name = f"{name} - {old_id}"
                    if frappe.db.exists("Shop", shop_name):
                        self.shop_id_map[old_id] = shop_name
                        continue

                    user = self.user_id_map.get(parts[1]) or "Administrator"

                    frappe.get_doc({
                        "doctype": "Shop", "shop_name": shop_name, "user": user, "uuid": old_id,
                        "status": "approved"
                    }).insert(ignore_permissions=True)
                    self.shop_id_map[old_id] = shop_name
                    print(f"Inserted Shop: {shop_name}")
                except Exception as e: print(f"Error shop: {e}")

    def _map_brand_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `brands` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, title = parts[0], self._clean_value(parts[2])
                    if not title: continue
                    if frappe.db.exists("Brand", title):
                        self.brand_id_map[old_id] = title
                        continue
                    doc = frappe.get_doc({"doctype": "Brand", "brand": title}).insert(ignore_permissions=True)
                    self.brand_id_map[old_id] = doc.name
                except Exception as e: print(f"Error brand: {e}")

    def _map_category_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `categories` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, title, parent_id = parts[0], self._clean_value(parts[2]), parts[4]
                    if not title: continue
                    if frappe.db.exists("Category", title):
                        self.category_id_map[old_id] = title
                        continue
                    parent = self.category_id_map.get(parent_id)
                    doc = frappe.get_doc({"doctype": "Category", "title": title, "parent_category": parent, "active": 1}).insert(ignore_permissions=True)
                    self.category_id_map[old_id] = doc.name
                except Exception as e: print(f"Error category: {e}")

    def _map_unit_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `units` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, name = parts[0], self._clean_value(parts[2])
                    if not name or frappe.db.exists("UOM", name):
                        self.unit_id_map[old_id] = name
                        continue
                    doc = frappe.get_doc({"doctype": "UOM", "uom_name": name}).insert(ignore_permissions=True)
                    self.unit_id_map[old_id] = doc.name
                except Exception as e: print(f"Error unit: {e}")

    def _map_product_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `products` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, title, cat_id, brand_id = parts[0], self._clean_value(parts[2]), parts[4], parts[6]
                    # Assuming Product autoname handles naming or we use title
                    if frappe.db.exists("Product", {"title": title}):
                        self.product_id_map[old_id] = frappe.db.get_value("Product", {"title": title}, "name")
                        continue
                    doc = frappe.get_doc({
                        "doctype": "Product", "title": title,
                        "category": self.category_id_map.get(cat_id),
                        "brand": self.brand_id_map.get(brand_id)
                    }).insert(ignore_permissions=True)
                    self.product_id_map[old_id] = doc.name
                except Exception as e: print(f"Error product: {e}")

    def _map_stock_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `stocks` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    stock_id, prod_id = parts[0], parts[1]
                    item_code = self.product_id_map.get(prod_id)
                    if item_code: self.stock_id_map[stock_id] = item_code
                except Exception as e: print(f"Error stock: {e}")

    def _map_shop_section_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `shop_sections` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, shop_id, area = parts[0], parts[1], self._clean_value(parts[2])
                    shop_name = self.shop_id_map.get(shop_id)
                    if not shop_name: continue
                    doc = frappe.get_doc({
                        "doctype": "Shop Section", "shop": shop_name, "area": area
                    }).insert(ignore_permissions=True)
                    self.shop_section_map[old_id] = doc.name
                except Exception as e: print(f"Error shop section: {e}")

    def _map_table_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `tables` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, name, section_id, chairs = parts[0], self._clean_value(parts[1]), parts[2], parts[3]
                    section_name = self.shop_section_map.get(section_id)
                    if not section_name: continue
                    doc = frappe.get_doc({
                        "doctype": "Table", "name": f"{name} - {old_id}", "shop_section": section_name,
                        "chair_count": int(chairs) if chairs else 0
                    }).insert(ignore_permissions=True)
                    self.table_map[old_id] = doc.name
                except Exception as e: print(f"Error table: {e}")

    def _map_parcel_order_setting_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `parcel_order_settings` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, type_name = parts[0], self._clean_value(parts[1])
                    price, price_km = parts[11], parts[12]
                    doc = frappe.get_doc({
                        "doctype": "Parcel Order Setting", "type": type_name,
                        "price": float(price), "price_per_km": float(price_km)
                    }).insert(ignore_permissions=True)
                    self.parcel_setting_map[old_id] = doc.name
                except Exception as e: print(f"Error parcel setting: {e}")

    def _map_parcel_option_data(self, opt_path, trans_path):
        titles = {}
        with open(trans_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `parcel_option_translations` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                parts = self._safe_split(v_str)
                if parts[2] == "'en'": titles[parts[1]] = self._clean_value(parts[3])

        for opt_id, title in titles.items():
            try:
                if frappe.db.exists("Parcel Option", {"title": title}):
                    doc = frappe.get_doc("Parcel Option", {"title": title})
                else:
                    doc = frappe.get_doc({
                        "doctype": "Parcel Option", "title": title, "price": 0
                    }).insert(ignore_permissions=True)
                self.parcel_option_map[opt_id] = doc.name
            except Exception as e: print(f"Error parcel option: {e}")

    def _map_user_address_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `user_addresses` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, title, user_id, address_json_str = parts[0], self._clean_value(parts[1]), parts[2], parts[3]
                    customer_email = self.user_id_map.get(user_id)
                    if not customer_email: continue

                    customer_name = frappe.db.get_value("Customer", {"email_id": customer_email}, "name")
                    if not customer_name:
                         u = frappe.get_doc("User", customer_email)
                         c = frappe.new_doc("Customer")
                         c.customer_name = u.full_name
                         c.email_id = customer_email
                         c.insert(ignore_permissions=True)
                         customer_name = c.name

                    address_line1 = "N/A"
                    try:
                        address_data = json.loads(address_json_str)
                        address_line1 = address_data.get('address') or "N/A"
                    except: pass

                    address_doc = {
                        "doctype": "Address", "address_title": title or customer_name,
                        "address_type": "Shipping", "address_line1": address_line1,
                        "city": "Musina", "country": "South Africa",
                        "links": [{"link_doctype": "Customer", "link_name": customer_name}]
                    }
                    self.addresses_to_insert.append((old_id, address_doc))
                except Exception as e: print(f"Error parsing address: {e}")

    def _insert_addresses(self):
        for old_id, address_doc in self.addresses_to_insert:
            try:
                if not frappe.db.exists("Address", {"address_title": address_doc["address_title"]}):
                    doc = frappe.get_doc(address_doc).insert(ignore_permissions=True)
                    self.user_address_map[old_id] = doc.name
            except Exception as e: print(f"Error inserting address: {e}")

    def _map_parcel_order_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `parcel_orders` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, user_id, total = parts[0], parts[1], parts[2]
                    status = self._clean_value(parts[7]).capitalize()
                    setting_id = parts[23]

                    user = self.user_id_map.get(user_id)
                    setting = self.parcel_setting_map.get(setting_id)
                    if not user or not setting: continue

                    frappe.get_doc({
                        "doctype": "Parcel Order", "user": user, "parcel_type": setting,
                        "total_price": float(total), "status": status,
                        "address_from": self._clean_value(parts[8]), "address_to": self._clean_value(parts[11]),
                        "phone_from": self._clean_value(parts[9]), "username_from": self._clean_value(parts[10]),
                        "phone_to": self._clean_value(parts[12]), "username_to": self._clean_value(parts[13]),
                        "delivery_fee": float(parts[14]), "delivery_date": self._clean_value(parts[17])
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error parcel order: {e}")

    def _map_booking_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `user_bookings` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    user_id, table_id = parts[2], parts[3]
                    start, end = self._clean_value(parts[4]), self._clean_value(parts[5])
                    status = self._clean_value(parts[7]).capitalize()

                    user = self.user_id_map.get(user_id)
                    table = self.table_map.get(table_id)
                    if not user or not table: continue

                    table_doc = frappe.get_doc("Table", table)
                    shop_section = frappe.get_doc("Shop Section", table_doc.shop_section)

                    frappe.get_doc({
                        "doctype": "Booking", "user": user, "shop": shop_section.shop, "table": table,
                        "booking_date": start.split(' ')[0] if start else None,
                        "start_time": start.split(' ')[1] if start else "00:00:00",
                        "end_time": end.split(' ')[1] if end else "00:00:00",
                        "status": status
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error booking: {e}")

    def _map_order_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `orders` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, user_id, shop_id, status = parts[0], parts[1], parts[6], self._clean_value(parts[9])

                    user = self.user_id_map.get(user_id)
                    shop = self.shop_id_map.get(shop_id)
                    if not user or not shop: continue

                    status_map = {"new": "New", "accepted": "Accepted", "delivered": "Delivered", "canceled": "Cancelled"}

                    self.orders_map[old_id] = {
                        "doctype": "Order", "user": user, "shop": shop,
                        "status": status_map.get(status, "New"),
                        "delivery_type": self._clean_value(parts[17]),
                        "order_items": []
                    }
                except Exception as e: print(f"Error order parsing: {e}")

    def _map_order_details_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `order_details` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    order_id, stock_id, price, qty = parts[1], parts[2], parts[3], parts[7]

                    if order_id not in self.orders_map: continue
                    item_code = self.stock_id_map.get(stock_id)
                    if not item_code: continue

                    self.orders_map[order_id]["order_items"].append({
                        "product": item_code, "quantity": int(qty), "price": float(price)
                    })
                except Exception as e: print(f"Error order detail: {e}")

    def _insert_orders(self):
        for old_id, order_data in self.orders_map.items():
            try:
                doc = frappe.get_doc(order_data)
                doc.insert(ignore_permissions=True)
                self.order_doc_map[old_id] = doc.name
                print(f"Inserted Order: {doc.name}")
            except Exception as e: print(f"Error inserting Order {old_id}: {e}")

    def _map_repeating_order_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `order_repeats` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_order_id, start_date = parts[1], self._clean_value(parts[2])
                    new_order_name = self.order_doc_map.get(old_order_id)
                    if not new_order_name: continue

                    order = frappe.get_doc("Order", new_order_name)
                    frappe.get_doc({
                        "doctype": "Repeating Order", "user": order.user, "original_order": new_order_name,
                        "start_date": start_date, "cron_pattern": "0 12 * * *", "is_active": 1
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error repeating order: {e}")

    def _map_banner_shops_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `banner_shops` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    shop_id, banner_id = parts[1], parts[2]
                    if banner_id not in self.banner_shop_map: self.banner_shop_map[banner_id] = []
                    self.banner_shop_map[banner_id].append(shop_id)
                except: pass

    def _map_banner_data(self, ban_path, trans_path):
        # Load translations
        trans = {}
        with open(trans_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `banner_translations` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                parts = self._safe_split(v_str)
                if parts[2] == "'en'":
                    trans[parts[1]] = {"title": self._clean_value(parts[3]), "description": self._clean_value(parts[4]), "button_text": self._clean_value(parts[5])}

        with open(ban_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `banners` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id = parts[0]
                    url = self._clean_value(parts[1])
                    img = self._clean_value(parts[3])
                    active = parts[4] == '1'

                    t_data = trans.get(old_id, {"title": f"Banner {old_id}"})
                    shop_ids = self.banner_shop_map.get(old_id, [])

                    # Helper to insert
                    def insert_banner(shop_val):
                        frappe.get_doc({
                            "doctype": "Banner", "shop": shop_val, "image": img, "link": url,
                            "title": t_data.get("title"), "description": t_data.get("description"),
                            "button_text": t_data.get("button_text"), "is_active": active
                        }).insert(ignore_permissions=True)

                    if shop_ids:
                        for sid in shop_ids:
                            sname = self.shop_id_map.get(sid)
                            if sname: insert_banner(sname)
                    else:
                        insert_banner(None) # Global
                except Exception as e: print(f"Error banner: {e}")

    def _map_coupon_data(self, coup_path, trans_path):
        trans = {}
        with open(trans_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `coupon_translations` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                parts = self._safe_split(v_str)
                if parts[2] == "'en'":
                    trans[parts[1]] = {"title": self._clean_value(parts[3]), "description": self._clean_value(parts[4])}

        with open(coup_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `coupons` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, shop_id, code = parts[0], parts[1], self._clean_value(parts[2])
                    ctype, qty, price, expire, for_what = self._clean_value(parts[3]), parts[4], parts[5], self._clean_value(parts[6]), self._clean_value(parts[11])

                    shop = self.shop_id_map.get(shop_id)
                    if not shop: continue

                    t_data = trans.get(old_id, {})

                    frappe.get_doc({
                        "doctype": "Coupon", "shop": shop, "code": code,
                        "title": t_data.get("title"), "description": t_data.get("description"),
                        "discount_type": "Percentage" if ctype == 'percent' else "Fixed",
                        "discount_amount": float(price), "quantity": int(qty),
                        "expired_at": expire, "applied_to": "Delivery Fee" if for_what == 'delivery_fee' else "Total Price"
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error coupon: {e}")

    def _map_receipt_data(self, rec_path, trans_path):
        trans = {}
        with open(trans_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `receipt_translations` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                parts = self._safe_split(v_str)
                if parts[2] == "'en'":
                    trans[parts[1]] = {"title": self._clean_value(parts[3]), "description": self._clean_value(parts[4])}

        with open(rec_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `receipts` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, shop_id, cat_id = parts[0], parts[1], parts[2]
                    img, active_t, total_t = self._clean_value(parts[5]), self._clean_value(parts[6]), self._clean_value(parts[7])
                    cal, serv = parts[8], parts[9]
                    bg_img = self._clean_value(parts[13])

                    shop = self.shop_id_map.get(shop_id)
                    cat = self.category_id_map.get(cat_id)
                    t_data = trans.get(old_id, {})

                    frappe.get_doc({
                        "doctype": "Receipt", "shop": shop, "category": cat,
                        "title": t_data.get("title", f"Recipe {old_id}"), "description": t_data.get("description"),
                        "image": img, "background_image": bg_img,
                        "active_time": active_t, "total_time": total_t,
                        "calories": int(cal) if cal else 0, "servings": int(serv) if serv else 1
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error receipt: {e}")

    def _map_story_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `stories` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    prod_id, shop_id, files = parts[1], parts[2], parts[4]

                    shop = self.shop_id_map.get(shop_id)
                    prod = self.product_id_map.get(prod_id)
                    if not shop: continue

                    urls = []
                    try: urls = json.loads(self._clean_value(files))
                    except: pass

                    if isinstance(urls, list):
                        for u in urls:
                             frappe.get_doc({
                                "doctype": "Story", "shop": shop, "product": prod,
                                "image": u, "is_active": 1
                             }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error story: {e}")

    def _map_wallet_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `wallets` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, uuid, user_id, balance = parts[0], self._clean_value(parts[1]), parts[2], parts[3]

                    user = self.user_id_map.get(user_id)
                    if not user: continue

                    if frappe.db.exists("Wallet", {"uuid": uuid}):
                        doc = frappe.get_doc("Wallet", {"uuid": uuid})
                    elif frappe.db.exists("Wallet", {"user": user}):
                        doc = frappe.get_doc("Wallet", {"user": user})
                        doc.uuid = uuid # Update UUID if existing
                        doc.balance = float(balance)
                        doc.save()
                    else:
                        doc = frappe.get_doc({
                            "doctype": "Wallet", "user": user, "uuid": uuid,
                            "balance": float(balance), "credit_balance": 0
                        }).insert(ignore_permissions=True)
                    self.wallet_uuid_map[uuid] = doc.name
                except Exception as e: print(f"Error wallet: {e}")

    def _map_transaction_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `transactions` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    old_id, payable_type, payable_id, price = parts[0], self._clean_value(parts[1]), parts[2], parts[3]
                    user_id, sys_id, trx_id = parts[4], parts[5], self._clean_value(parts[6])
                    note, perform_time, status = self._clean_value(parts[7]), self._clean_value(parts[8]), self._clean_value(parts[10])
                    status_desc, type_val, request = self._clean_value(parts[11]), self._clean_value(parts[16]), self._clean_value(parts[15])

                    user = self.user_id_map.get(user_id)
                    if not user: continue

                    gateway = self.payment_gateway_map.get(str(sys_id))

                    doc = frappe.get_doc({
                        "doctype": "Transaction", "user": user, "amount": float(price),
                        "status": status, "payable_type": payable_type, "payable_id": int(payable_id),
                        "payment_gateway": gateway, "payment_reference": trx_id,
                        "note": note, "status_description": status_desc,
                        "performed_at": perform_time, "type": type_val,
                        "request_data": request
                    }).insert(ignore_permissions=True)
                    self.transaction_id_map[old_id] = doc.name # Fixed: Store new doc name
                except Exception as e: print(f"Error transaction: {e}")

    def _map_wallet_history_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `wallet_histories` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    # id, uuid, wallet_uuid, transaction_id, type, price, note, status, created_by...
                    wallet_uuid, trans_id = self._clean_value(parts[2]), parts[3]
                    type_val, price, note, status = self._clean_value(parts[4]), parts[5], self._clean_value(parts[6]), self._clean_value(parts[7])

                    wallet = self.wallet_uuid_map.get(wallet_uuid)
                    if not wallet: continue

                    trans_ref = self.transaction_id_map.get(trans_id) if trans_id and trans_id != 'NULL' else None

                    frappe.get_doc({
                        "doctype": "Wallet History", "wallet": wallet, "amount": float(price),
                        "transaction_type": type_val.capitalize(),
                        "status": status.capitalize(), "description": note,
                        "transaction_ref": trans_ref
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error wallet history: {e}")

    def _map_payout_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `payouts` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    status, created_by, approved_by = self._clean_value(parts[1]).capitalize(), parts[2], parts[3]
                    payment_id, cause, answer, price = parts[5], self._clean_value(parts[6]), self._clean_value(parts[7]), parts[8]
                    date = self._clean_value(parts[9])

                    creator = self.user_id_map.get(created_by)
                    approver = self.user_id_map.get(approved_by)

                    # Find shop for creator
                    shop = None
                    if creator:
                        shop = frappe.db.get_value("Shop", {"user": creator}, "name")

                    if not shop: continue

                    gateway = self.payment_gateway_map.get(str(payment_id))

                    frappe.get_doc({
                        "doctype": "Payout", "shop": shop, "amount": float(price),
                        "status": status, "payment_date": date.split(' ')[0] if date else now(),
                        "approved_by": approver, "payment_method": gateway,
                        "reason": cause, "response": answer
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error payout: {e}")

    def _map_shop_subscription_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        for values_str in re.findall(r"INSERT INTO `shop_subscriptions` VALUES \((.*?)\);", content):
            for v_str in re.findall(r"\((.*?)\)", values_str):
                try:
                    parts = self._safe_split(v_str)
                    shop_id, sub_id, expire, price, type_val = parts[1], parts[2], self._clean_value(parts[3]), parts[4], self._clean_value(parts[5])
                    active = parts[6] == '1'

                    shop = self.shop_id_map.get(shop_id)
                    if not shop: continue

                    plan_name = f"Plan {sub_id}"
                    if not frappe.db.exists("Subscription", {"name": plan_name}):
                         frappe.get_doc({"doctype": "Subscription", "type": type_val or "orders", "price": float(price), "month": 1, "active": 1}).insert(ignore_permissions=True)
                         # Note: Subscription DocType has auto-name? No, checked json, no autoname. But id is implicit.
                         # Wait, Subscription json has NO autoname field. So it uses hash.
                         # But I need to link it.
                         # Actually, I should create it and use the name.

                    # Re-fetching or relying on creation. Let's assume we create it if not exists by some criteria.
                    # Since Subscription has no unique name field in my previous check, I'll just create new ones if needed or try to reuse.
                    # For seed simplicity, I'll create one.

                    sub_doc = frappe.get_doc({"doctype": "Subscription", "type": type_val or "orders", "price": float(price), "month": 1, "active": 1}).insert(ignore_permissions=True)

                    frappe.get_doc({
                        "doctype": "Shop Subscription", "shop": shop, "subscription": sub_doc.name,
                        "expired_at": expire, "price": float(price), "type": type_val,
                        "active": active
                    }).insert(ignore_permissions=True)
                except Exception as e: print(f"Error shop subscription: {e}")

    def _ensure_payment_gateways(self):
        for gw_id, gw_name in self.payment_gateway_map.items():
            if not frappe.db.exists("PaaS Payment Gateway", {"gateway_controller": gw_name}):
                frappe.get_doc({
                    "doctype": "PaaS Payment Gateway",
                    "gateway_controller": gw_name,
                    "enabled": 1
                }).insert(ignore_permissions=True)

    def run(self):
        frappe.local.user = frappe.get_doc("User", "Administrator")
        print("--- Seeder Started ---")

        self._ensure_payment_gateways()
        frappe.db.commit()

        self._map_user_data(os.path.join(self.db_path, 'users.sql'))
        frappe.db.commit()

        self._map_shop_data(os.path.join(self.db_path, 'shops.sql'))
        frappe.db.commit()

        self._map_brand_data(os.path.join(self.db_path, 'brands.sql'))
        self._map_category_data(os.path.join(self.db_path, 'categories.sql'))
        self._map_unit_data(os.path.join(self.db_path, 'units.sql'))
        frappe.db.commit()

        self._map_product_data(os.path.join(self.db_path, 'products.sql'))
        self._map_stock_data(os.path.join(self.db_path, 'stocks.sql'))
        frappe.db.commit()

        self._map_shop_section_data(os.path.join(self.db_path, 'shop_sections.sql'))
        self._map_table_data(os.path.join(self.db_path, 'tables.sql'))
        frappe.db.commit()

        self._map_parcel_order_setting_data(os.path.join(self.db_path, 'parcel_order_settings.sql'))
        self._map_parcel_option_data(os.path.join(self.db_path, 'parcel_options.sql'), os.path.join(self.db_path, 'parcel_option_translations.sql'))
        frappe.db.commit()

        self._map_user_address_data(os.path.join(self.db_path, 'user_addresses.sql'))
        self._insert_addresses()
        frappe.db.commit()

        self._map_parcel_order_data(os.path.join(self.db_path, 'parcel_orders.sql'))
        self._map_booking_data(os.path.join(self.db_path, 'user_bookings.sql'))
        frappe.db.commit()

        self._map_order_data(os.path.join(self.db_path, 'orders.sql'))
        self._map_order_details_data(os.path.join(self.db_path, 'order_details.sql'))
        self._insert_orders()
        frappe.db.commit()

        self._map_repeating_order_data(os.path.join(self.db_path, 'order_repeats.sql'))
        frappe.db.commit()

        # Marketing
        self._map_banner_shops_data(os.path.join(self.db_path, 'banner_shops.sql'))
        self._map_banner_data(os.path.join(self.db_path, 'banners.sql'), os.path.join(self.db_path, 'banner_translations.sql'))
        self._map_coupon_data(os.path.join(self.db_path, 'coupons.sql'), os.path.join(self.db_path, 'coupon_translations.sql'))
        self._map_receipt_data(os.path.join(self.db_path, 'receipts.sql'), os.path.join(self.db_path, 'receipt_translations.sql'))
        self._map_story_data(os.path.join(self.db_path, 'stories.sql'))
        frappe.db.commit()

        # Finance
        self._map_wallet_data(os.path.join(self.db_path, 'wallets.sql'))
        frappe.db.commit()
        self._map_transaction_data(os.path.join(self.db_path, 'transactions.sql'))
        frappe.db.commit()
        self._map_wallet_history_data(os.path.join(self.db_path, 'wallet_histories.sql'))
        frappe.db.commit()
        self._map_payout_data(os.path.join(self.db_path, 'payouts.sql'))
        frappe.db.commit()
        self._map_shop_subscription_data(os.path.join(self.db_path, 'shop_subscriptions.sql'))
        frappe.db.commit()

        print("--- Seeder Completed ---")

def run_seeder():
    if frappe.local.site != "juvo.tenant.rokct.ai":
        print(f"Skipping seeder for site {frappe.local.site}")
        return
    LegacyDataSeeder(frappe.local.site, os.path.join(get_bench_path(), "apps/paas/paas/db")).run()

if __name__ == "__main__": run_seeder()
