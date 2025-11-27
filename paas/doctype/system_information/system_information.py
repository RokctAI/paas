import frappe
from frappe.model.document import Document
import json
import os

class SystemInformation(Document):
    def onload(self):
        # Core Version (Frappe)
        self.core = f"Frappe {frappe.__version__}"

        # PaaS Version from paas/versions.json
        paas_versions_file = frappe.get_app_path("paas", "versions.json")
        
        try:
            with open(paas_versions_file, "r") as f:
                paas_versions = json.load(f)
            self.paas = paas_versions.get("paas", "Unknown")
        except Exception:
            self.paas = "Error reading paas versions.json"

        # Other App Versions from rokct/versions.json
        rokct_versions_file = frappe.get_app_path("rokct", "versions.json")

        try:
            with open(rokct_versions_file, "r") as f:
                versions = json.load(f)

            self.rokct = versions.get("rokct", "Unknown")
            self.brain = versions.get("brain", "Unknown")
            self.payments = versions.get("payments", "Unknown")
            self.flutter_sdk_version = versions.get("flutter_sdk_version", "Unknown")

        except Exception:
            self.rokct = "Error reading rokct versions.json"
            self.brain = "Error"
            self.payments = "Error"
            self.flutter_sdk_version = "Error"

        # Latest Error
        try:
            latest_log = frappe.get_all("Error Log", limit=1, order_by="creation desc", fields=["error", "method", "creation"])
            if latest_log:
                log = latest_log[0]
                self.latest_error = f"{log.creation}: {log.method}\n{log.error}"
            else:
                self.latest_error = "No errors found."
        except Exception:
            self.latest_error = "Could not fetch error logs."
