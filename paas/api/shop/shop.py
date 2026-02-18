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
    t_shop = frappe.qb.DocType("Shop")
    query = (
        frappe.qb.from_(t_shop)
        .select(
            t_shop.name, t_shop.uuid, t_shop.slug, t_shop.user, t_shop.logo, t_shop.cover_photo,
            t_shop.phone, t_shop.address, t_shop.location, t_shop.status, t_shop.type, t_shop.min_amount,
            t_shop.tax, t_shop.delivery_time_type, t_shop.delivery_time_from, t_shop.delivery_time_to,
            t_shop.open, t_shop.visibility, t_shop.verify, t_shop.service_fee, t_shop.percentage, t_shop.enable_cod,
            t_shop.shop_type, t_shop.is_ecommerce
        )
        .where(t_shop.open == 1)
        .where(t_shop.status == "approved")
        .where(t_shop.visibility == 1)
    )

    if category_id:
        query = query.where(t_shop.category == category_id)

    from frappe.query_builder.functions import Function
    to_tsvector = Function("to_tsvector")
    plainto_tsquery = Function("plainto_tsquery")
    query = query.where(
        to_tsvector("english", t_shop.shop_name).matches(plainto_tsquery("english", search))
    )

    shops = query.limit(limit_page_length).offset(limit_start).orderby(t_shop.shop_name).run(as_dict=True)

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
def get_nearby_shops(latitude: float, longitude: float, radius_km: float = 10, lang: str = "en"):
    """
    Retrieves a list of shops within a given radius.
    """
    if latitude is None or longitude is None:
         return get_shops()

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
    
    # helper to get shop details efficiently? 
    # For now we get IDs and then re-fetch full details or just return what's needed?
    # The original returned shop objects. `get_shops` formats them nicely.
    # Let's get the IDs that match and then call `get_shops` with a filter or manually format.
    # The original implementation returned the raw shop objects from the loop, 
    # but `get_shops` returns api_response(data=formatted).
    # The original __init__.py `get_nearby_shops` returned a LIST of shop objects (dicts).
    
    nearby_shop_ids = []
    for shop in shops:
        if shop.is_ecommerce:
             nearby_shop_ids.append(shop.name)
             continue

        if shop.latitude and shop.longitude:
            try:
                distance = haversine(float(latitude), float(longitude), float(shop.latitude), float(shop.longitude))
                if distance <= float(radius_km):
                    nearby_shop_ids.append(shop.name)
            except:
                continue

    # Now use generic get_shops_by_ids to return formatted data
    return get_shops_by_ids(shop_ids=nearby_shop_ids)


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
def get_shops_recommend(latitude: float, longitude: float, lang: str = "en"):
    """
    Returns recommended shops based on location and rating.
    """
@frappe.whitelist(allow_guest=True)
def get_nearest_delivery_points(latitude: float, longitude: float, radius_km: float = 50):
    """
    Retrieves a list of active Delivery Points within a given radius.
    """
    if latitude is None or longitude is None:
        frappe.throw("Latitude and Longitude are required.", frappe.ValidationError)

    try:
        lat = float(latitude)
        lon = float(longitude)
    except ValueError:
        frappe.throw("Invalid Latitude or Longitude format.", frappe.ValidationError)

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

    # Fetch all active delivery points
    points = frappe.get_all("Delivery Point", 
                            filters={"active": 1}, 
                            fields=["name", "latitude", "longitude", "address", "price", "active"])
    
    nearby_points = []
    for point in points:
        if point.latitude and point.longitude:
            try:
                dist = haversine(lat, lon, float(point.latitude), float(point.longitude))
                if dist <= float(radius_km):
                    # Add distance to the point object for sorting/info
                    point["distance_km"] = round(dist, 2)
                    nearby_points.append(point)
            except (ValueError, TypeError):
                continue

    # Sort by distance
    nearby_points.sort(key=lambda x: x["distance_km"])

    return nearby_points
