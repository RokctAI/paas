# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DeliveryZone(Document):
    def validate(self):
        if self.delivery_fee < 0:
            frappe.throw("Delivery Fee cannot be negative")
        
        if not self.coordinates:
            frappe.throw("Coordinates are required for a delivery zone")
