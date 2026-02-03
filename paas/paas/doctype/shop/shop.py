import frappe
from frappe.model.document import Document


class Shop(Document):
	def after_insert(self):
		self.create_shop_warehouse()

	def create_shop_warehouse(self):
		"""
		Automatically creates a unique warehouse for the shop if it doesn't have one.
		"""
		if self.warehouse:
			return

		warehouse_name = f"{self.shop_name} - Warehouse"
		
		# Ensure Warehouse Type 'Store' exists
		if not frappe.db.exists("Warehouse Type", "Store"):
			frappe.get_doc({
				"doctype": "Warehouse Type",
				"name": "Store"
			}).insert(ignore_permissions=True)

		# Get default company
		company = frappe.db.get_single_value("Global Settings", "default_company")
		if not company:
			# Fallback to any company if no default is set
			companies = frappe.get_all("Company", limit=1)
			if companies:
				company = companies[0].name
			else:
				# This shouldn't happen in a provisioned site, but let's be safe
				frappe.log_error(f"No company found during warehouse creation for Shop {self.name}", "Shop Warehouse Error")
				return

		# Create Warehouse
		if not frappe.db.exists("Warehouse", warehouse_name):
			warehouse = frappe.get_doc({
				"doctype": "Warehouse",
				"warehouse_name": self.shop_name,
				"company": company,
				"warehouse_type": "Store",
				"is_group": 0
			}).insert(ignore_permissions=True)
			
			self.db_set("warehouse", warehouse.name)
			frappe.db.commit()
