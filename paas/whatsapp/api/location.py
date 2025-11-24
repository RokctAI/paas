# Copyright (c) 2025, ROKCT and contributors
# For license information, please see license.txt

import frappe
import json
from paas.whatsapp.responses import send_static_map_confirmation

def handle_location(lat, long, session):
    """
    Handles Geo-Location updates.
    """
    # 1. Update Session Location
    session.location = json.dumps({"lat": lat, "long": long})
    session.save(ignore_permissions=True)
    
    # 2. Send Confirmation Map
    send_static_map_confirmation(session.wa_id, lat, long)
