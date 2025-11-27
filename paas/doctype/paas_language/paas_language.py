# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaaSLanguage(Document):
    def validate(self):
        if self.default:
            # Ensure only one default language exists
            frappe.db.sql("""UPDATE `tabPaaS Language` SET `default` = 0 WHERE name != %s""", self.name)
