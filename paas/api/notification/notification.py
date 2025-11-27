import frappe
import json
import requests

@frappe.whitelist()
def send_push_notification(user: str, title: str, body: str, data: dict = None):
    """
    Sends a push notification to a specific user via FCM.
    """
    try:
        settings = frappe.get_single("Push Notification Settings")
        if not settings.server_key:
            frappe.log_error("FCM Server Key is missing in Push Notification Settings", "Push Notification Error")
            return {"status": "failed", "message": "Server key missing."}

        tokens = frappe.get_all("Device Token", filters={"user": user}, pluck="device_token")
        if not tokens:
            return {"status": "failed", "message": "No device tokens found for user."}

        headers = {
            "Authorization": f"key={settings.server_key}",
            "Content-Type": "application/json"
        }

        success_count = 0
        failure_count = 0

        for token in tokens:
            payload = {
                "to": token,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data or {}
            }

            try:
                response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=payload, timeout=5)
                if response.status_code == 200:
                    success_count += 1
                else:
                    failure_count += 1
                    frappe.log_error(f"FCM Error for {token}: {response.text}", "Push Notification Error")
            except Exception as e:
                failure_count += 1
                frappe.log_error(f"Request Error for {token}: {str(e)}", "Push Notification Error")

        return {
            "status": "success",
            "message": f"Sent: {success_count}, Failed: {failure_count}",
            "details": {"sent": success_count, "failed": failure_count}
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Push Notification Exception")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def get_default_sms_payload():
    """
    Returns the default SMS payload from Push Notification Settings.
    """
    settings = frappe.get_single("Push Notification Settings")

    payload = {
        "default": True,
        "api_key": settings.api_key,
        "ios_api_key": settings.ios_api_key,
        "android_api_key": settings.android_api_key,
        "server_key": settings.server_key,
        "vapid_key": settings.vapid_key,
        "auth_domain": settings.auth_domain,
        "project_id": settings.project_id,
        "storage_bucket": settings.storage_bucket,
        "message_sender_id": settings.messaging_sender_id,
        "app_id": settings.app_id,
        "measurement_id": settings.measurement_id
    }

    return json.dumps(payload)
