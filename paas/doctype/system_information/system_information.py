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

        # 1. Flutter SDK Version from local rcore/versions.json
        self.flutter_sdk_version = "Unknown"
        try:
            rcore_versions_file = frappe.get_app_path("rcore", "versions.json")
            if os.path.exists(rcore_versions_file):
                with open(rcore_versions_file, "r") as f:
                    rcore_versions = json.load(f)
                self.flutter_sdk_version = rcore_versions.get("flutter_sdk_version", "Unknown")
        except Exception:
            self.flutter_sdk_version = "Error reading rcore/versions.json"

        # 2. ALL App Versions from platform.rokct.ai API
        # Since Control site has ALL apps (Control, Brain, Payments) installed, we trust its reporting.
        self.control = "Unavailable"
        self.brain = "N/A"
        self.payments = "N/A"

        try:
            import requests
            # Get the control platform URL from site config
            control_url = frappe.conf.get("control_url", "https://platform.rokct.ai")
            api_endpoint = f"{control_url}/api/method/control.control.api.versions.get_versions"
            
            response = requests.get(api_endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                api_versions = data.get("message", {})
                
                if isinstance(api_versions, dict):
                    def get_ver(app_name):
                        app_data = api_versions.get(app_name, {})
                        if isinstance(app_data, dict):
                            return app_data.get("version", "N/A")
                        return "N/A"

                    self.control = get_ver("control")
                    self.brain = get_ver("brain")
                    self.payments = get_ver("payments")
                    
        except Exception as e:
            frappe.log_error(f"Failed to fetch control versions: {str(e)}", "System Information API Error")

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
