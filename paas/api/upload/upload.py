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

@frappe.whitelist()
def upload_multi_image():
    """
    Uploads multiple images.
    Expects request.files to contain the files.
    """
    files = frappe.request.files
    uploaded_files = []
    
    if not files:
        return api_response(message="No files found", status_code=400)

    for key, file in files.items():
        try:
            file_doc = save_file(
                fname=file.filename,
                content=file.read(),
                dt=None,
                dn=None,
                is_private=0
            )
            uploaded_files.append(file_doc.file_url)
        except Exception as e:
            frappe.log_error(f"Multi-upload failed for {file.filename}: {e}")
            continue

    return api_response(data=uploaded_files)
