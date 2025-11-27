import frappe
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def upload_file(file, filename=None, is_private=0):
    """
    Uploads a file and returns the file URL.
    """
    try:
        # Save the file using Frappe's file manager
        file_doc = save_file(
            fname=filename or file.filename,
            content=file.read(),
            dt=None,  # Not attached to any doctype
            dn=None,
            is_private=is_private
        )
        
        return {
            "file_url": file_doc.file_url,
            "file_name": file_doc.file_name,
            "name": file_doc.name
        }
    except Exception as e:
        frappe.log_error(f"File upload failed: {str(e)}")
        frappe.throw(f"Failed to upload file: {str(e)}")
