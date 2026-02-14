# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaaSLanguage(Document):
    def validate(self):
        if self.default:
            # Ensure only one default language exists
            t_paas_lang = frappe.qb.DocType("PaaS Language")
            (
                frappe.qb.update(t_paas_lang)
                .set(t_paas_lang.default, 0)
                .where(t_paas_lang.name != self.name)
            ).run()
