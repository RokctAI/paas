# Copyright (c) 2025, ROKCT and contributors
# For license information, please see license.txt

import frappe
from paas.paas.whatsapp.utils import get_or_create_session
from paas.paas.whatsapp.responses import send_text, send_cart_summary
from paas.paas.whatsapp.api.location import handle_location
from paas.paas.whatsapp.api.shop import handle_interactive

def handle_message(message, wa_id, profile_name):
    """
    Dispatches the message based on its type.
    """
    msg_type = message.get('type')
    session = get_or_create_session(wa_id)
    
    if msg_type == 'text':
        text = message['text']['body'].lower()
        handle_text(text, session)
        
    elif msg_type == 'location':
        loc = message['location']
        handle_location(loc['latitude'], loc['longitude'], session)
        
    elif msg_type == 'interactive':
        reply = message['interactive']
        handle_interactive(reply, session)

def handle_text(text, session):
    text = text.lower().strip()
    
    if text in ['hi', 'hello', 'menu', 'start']:
        greeting = "👋 Hello!"
        if session.linked_user:
            first_name = frappe.db.get_value("User", session.linked_user, "first_name")
            if first_name:
                greeting = f"👋 Welcome back, {first_name}!"
        
        send_text(session.wa_id, f"{greeting} Please share your location to find shops near you.\n\nTap 📎 -> Location -> Send Current Location.")
        
    elif text in ['cart', 'checkout', 'basket']:
        send_cart_summary(session.wa_id, session)
        
    elif session.current_flow == 'checkout_address_input':
        # Routing text as Address Input
        from paas.paas.whatsapp.api.checkout import handle_checkout_action
        handle_checkout_action(session, 'address_input', payload=text)
        
    else:
        # Default fallback
        send_text(session.wa_id, "I didn't understand that. Type 'Hi' to start or 'Cart' to view your items.")
