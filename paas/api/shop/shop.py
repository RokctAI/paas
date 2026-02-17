# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import uuid
from paas.api.utils import api_response

@frappe.whitelist()
def create_shop(shop_data):
    """
    Creates a new Shop document.
    Only users with 'System Manager' or 'Seller' roles can create a shop.
    """
    if "System Manager" not in frappe.get_roles() and "Seller" not in frappe.get_roles():
        frappe.throw("You are not authorized to create a shop.", frappe.PermissionError)

    if not isinstance(shop_data, dict):
        frappe.throw("shop_data must be a dictionary.", frappe.ValidationError)

    # Set the current user as the owner if not specified
    if 'user' not in shop_data:
        shop_data['user'] = frappe.session.user

    # Generate UUID and slug
    shop_data['uuid'] = str(uuid.uuid4())
    shop_data['slug'] = frappe.utils.slug(shop_data.get('shop_name'))

    try:
        shop = frappe.get_doc({
            "doctype": "Shop",
            **shop_data
        })
        shop.insert(ignore_permissions=True)
        frappe.db.commit()
        return api_response(data=shop.as_dict(), message="Shop created successfully")
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Shop Creation Failed")
        frappe.throw(f"An error occurred while creating the shop: {e}")

@frappe.whitelist(allow_guest=True)
def get_shops(limit_start: int = 0, limit_page_length: int = 20, order_by: str = "name", order: str = "desc", **kwargs):
    """
    Retrieves a list of shops with pagination and filters.
    """

    filters = {
        "status": "approved",
        "visibility": 1,
        "open": 1
    }

    if kwargs.get("delivery"):
        filters["delivery"] = 1

    if kwargs.get("takeaway"):
        filters["pickup"] = 1

    shops = frappe.get_list(
        "Shop",
        filters=filters,
        fields=[
            "name", "uuid", "slug", "user", "logo", "cover_photo",
            "phone", "address", "location", "status", "type", "min_amount",
            "tax", "delivery_time_type", "delivery_time_from", "delivery_time_to",
            "open", "visibility", "verify", "service_fee", "percentage", "enable_cod",
            "shop_type", "is_ecommerce"
        ],
        offset=limit_start,
        limit=limit_page_length,
        order_by=f"{order_by} {order}"
    )

    # Global COD Check
    cash_gateway = frappe.db.get_value("PaaS Payment Gateway", {"gateway_controller": "Cash", "enabled": 1})
    is_global_cod_enabled = bool(cash_gateway)

    # Replicating the structure of the legacy ShopResource
    formatted_shops = []
    for shop in shops:
        # Hierarchical COD: Global AND Shop
        is_cod = is_global_cod_enabled and (shop.enable_cod if shop.enable_cod is not None else 1)
        
        formatted_shops.append({
            'id': shop.name,
            'uuid': shop.uuid,
            'slug': shop.slug,
            'user_id': shop.user,
            'tax': shop.tax,
            'service_fee': shop.service_fee,
            'percentage': shop.percentage,
            'phone': shop.phone,
            'open': bool(shop.open),
            'visibility': bool(shop.visibility),
            'verify': bool(shop.verify),
            'logo_img': shop.logo,
            'background_img': shop.cover_photo,
            'min_amount': shop.min_amount,
            'status': shop.status,
            'enable_cod': bool(is_cod),
            'type': shop.shop_type or shop.type, # Map new shop_type to legacy type field
            'shop_type': shop.shop_type,
            'is_ecommerce': bool(shop.is_ecommerce),
            'delivery_time': {
                'type': shop.delivery_time_type,
                'from': shop.delivery_time_from,
                'to': shop.delivery_time_to
            },
            'location': shop.location,
            'translation': {
                'title': shop.name,
                'address': shop.address
            }
        })

    return api_response(data=formatted_shops)

@frappe.whitelist(allow_guest=True)
def get_shop_details(uuid: str):
    """
    Retrieves a single shop by its UUID.
    """
    shop = frappe.get_doc("Shop", {"uuid": uuid})

    if not shop:
        frappe.throw(f"Shop with UUID {uuid} not found.", frappe.DoesNotExistError)

    # Global COD Check
    cash_gateway = frappe.db.get_value("PaaS Payment Gateway", {"gateway_controller": "Cash", "enabled": 1})
    is_global_cod_enabled = bool(cash_gateway)
    
    # Hierarchical COD: Global AND Shop
    # Note: shop object from get_doc has attributes directly
    is_cod = is_global_cod_enabled and (shop.enable_cod if shop.enable_cod is not None else 1)

    # Replicating the structure of the legacy ShopResource
    return api_response(data={
        'id': shop.name,
        'uuid': shop.uuid,
        'slug': shop.slug,
        'user_id': shop.user,
        'tax': shop.tax,
        'service_fee': shop.service_fee,
        'percentage': shop.percentage,
        'phone': shop.phone,
        'open': bool(shop.open),
        'visibility': bool(shop.visibility),
        'verify': bool(shop.verify),
        'logo_img': shop.logo,
        'background_img': shop.cover_photo,
        'min_amount': shop.min_amount,
        'status': shop.status,
        'enable_cod': bool(is_cod),
        'type': shop.shop_type or shop.type, # Map new shop_type to legacy type field
        'shop_type': shop.shop_type,
        'is_ecommerce': bool(shop.is_ecommerce),
        'delivery_time': {
            'type': shop.delivery_time_type,
            'from': shop.delivery_time_from,
            'to': shop.delivery_time_to
        },
        'location': shop.location,
        'translation': {
            'title': shop.name,
            'address': shop.address
        }
    })

@frappe.whitelist(allow_guest=True)
def search_shops(search: str, category_id: int = None, limit_start: int = 0, limit_page_length: int = 20):
    """
    Searches for shops by name, optionally filtered by category.
    """
    filters = [
        ["Shop", "shop_name", "like", f"%{search}%"],
        ["Shop", "open", "=", 1],
        ["Shop", "status", "=", "approved"],
        ["Shop", "visibility", "=", 1]
    ]

    if category_id:
        filters.append(["Shop", "category", "=", category_id])

    shops = frappe.get_list(
        "Shop",
        filters=filters,
        fields=[
            "name", "uuid", "slug", "user", "logo", "cover_photo",
            "phone", "address", "location", "status", "type", "min_amount",
            "tax", "delivery_time_type", "delivery_time_from", "delivery_time_to",
            "open", "visibility", "verify", "service_fee", "percentage", "enable_cod",
            "shop_type", "is_ecommerce"
        ],
        offset=limit_start,
        limit=limit_page_length,
        order_by="shop_name"
    )

    # Global COD Check
    cash_gateway = frappe.db.get_value("PaaS Payment Gateway", {"gateway_controller": "Cash", "enabled": 1})
    is_global_cod_enabled = bool(cash_gateway)

    formatted_shops = []
    for shop in shops:
        # Hierarchical COD: Global AND Shop
        is_cod = is_global_cod_enabled and (shop.enable_cod if shop.enable_cod is not None else 1)
        
        formatted_shops.append({
            'id': shop.name,
            'uuid': shop.uuid,
            'slug': shop.slug,
            'user_id': shop.user,
            'tax': shop.tax,
            'service_fee': shop.service_fee,
            'percentage': shop.percentage,
            'phone': shop.phone,
            'open': bool(shop.open),
            'visibility': bool(shop.visibility),
            'verify': bool(shop.verify),
            'logo_img': shop.logo,
            'background_img': shop.cover_photo,
            'min_amount': shop.min_amount,
            'status': shop.status,
            'enable_cod': bool(is_cod),
            'type': shop.shop_type or shop.type, # Map new shop_type to legacy type field
            'shop_type': shop.shop_type,
            'is_ecommerce': bool(shop.is_ecommerce),
            'delivery_time': {
                'type': shop.delivery_time_type,
                'from': shop.delivery_time_from,
                'to': shop.delivery_time_to
            },
            'location': shop.location,
            'translation': {
                'title': shop.name,
                'address': shop.address
            }
        })

    return api_response(data=formatted_shops)

@frappe.whitelist(allow_guest=True)
def get_shop_types():
    """
    Retrieves all available Shop Types.
    """
    types = frappe.get_all("Shop Type", fields=["name", "title", "description", "icon"], order_by="title asc")
    return api_response(data=types)


@frappe.whitelist(allow_guest=True)
def get_nearby_shops(clientLocation=None):
    """
    Retrieves shops near the provided location.
    clientLocation: "lat,long" string.
    """
    # For now, return all shops or reuse get_shops logic.
    # TODO: Implement geospatial search
    return get_shops()


@frappe.whitelist(allow_guest=True)
def check_driver_zone(shop_id=None, address=None):
    """
    Checks if the address is within the shop's delivery zone.
    Expects address as dict/json with latitude/longitude.
    """
    # Mock response: Always reachable for now
    return api_response(data={"status": True, "distance": 1.2})


@frappe.whitelist(allow_guest=True)
def get_shops_by_ids(shop_ids: list = None, **kwargs):
    """
    Retrieves shops by a list of IDs.
    """
    filters = {}
    ids_to_filter = shop_ids
    
    # Handle possible JSON string or alternative kwarg
    if kwargs.get("shops"):
        try:
             import json
             ids_to_filter = json.loads(kwargs.get("shops")) if isinstance(kwargs.get("shops"), str) else kwargs.get("shops")
        except:
             ids_to_filter = None

    if not ids_to_filter:
        return api_response(data=[])

    shops = frappe.get_list(
        "Shop",
        filters={"name": ["in", ids_to_filter]},
        fields=[
            "name", "uuid", "slug", "user", "logo", "cover_photo",
            "phone", "address", "location", "status", "type", "min_amount",
            "tax", "delivery_time_type", "delivery_time_from", "delivery_time_to",
            "open", "visibility", "verify", "service_fee", "percentage", "enable_cod",
            "shop_type", "is_ecommerce"
        ]
    )
    
    # Simple formatter (reuse get_shops logic ideally, but keep simple here)
    formatted_shops = []
    for shop in shops:
        formatted_shops.append({
            'id': shop.name,
            'uuid': shop.uuid,
            'slug': shop.slug,
            'logo_img': shop.logo,
            'background_img': shop.cover_photo,
             'translation': {
                'title': shop.name,
                'address': shop.address
            }
        })
        
    return api_response(data=formatted_shops)
