# Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmailSettings(Document):
	def onload(self):
		if not self.sender_email:
			self.relay_status = "Using Email Relay"
		else:
			self.relay_status = "Configured"
