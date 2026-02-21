import frappe
import json
from frappe.utils import cint
from frappe import _
from paas.api.utils import _require_admin

def _api_success(data=None, message=""):
    return {
        "status": True,
        "message": message,
        "data": data,
        "timestamp": frappe.utils.now_datetime().isoformat()
    }

def _api_error(message="", status_code=500):
    frappe.local.response['http_status_code'] = status_code
    return {
        "status": False,
        "message": message,
        "timestamp": frappe.utils.now_datetime().isoformat()
    }

@frappe.whitelist(allow_guest=True)
def get_mobile_translations(lang=None):
    target_lang = lang or "en"

    translations = frappe.get_all("PaaS Translation",
                                  filters={"locale": target_lang, "status": 1},
                                  fields=["key", "value"])

    result = {t["key"]: t["value"] for t in translations}

    return _api_success(result, message="Successfully fetched")

@frappe.whitelist()
def get_translations_paginate(search=None, group=None, locale=None, perPage=10, page=1, **kwargs):
    _require_admin()

    per_page = cint(perPage)
    current_page = cint(page)
    start = (current_page - 1) * per_page

    t_translation = frappe.qb.DocType("PaaS Translation")

    # Base query for filtering
    base_query = frappe.qb.from_(t_translation)

    if group:
        base_query = base_query.where(t_translation.group == group)
    if locale:
        base_query = base_query.where(t_translation.locale == locale)
    if search:
        base_query = base_query.where(
            (t_translation.key.like(f"%{search}%")) 
            | (t_translation.value.like(f"%{search}%"))
        )

    # Count total distinct keys
    count_query = base_query.select(frappe.qb.fn.Count(frappe.qb.fn.Distinct(t_translation.key)))
    total_keys = count_query.run()[0][0]

    if total_keys == 0:
        return _api_success({
            "total": 0,
            "perPage": per_page,
            "translations": {}
            })

    # Get paginated distinct keys
    keys_query = base_query.select(frappe.qb.fn.Distinct(t_translation.key))
    keys_query = keys_query.orderby(t_translation.key, order=frappe.qb.asc).limit(per_page).offset(start)
    paginated_keys = keys_query.run(as_dict=True)

    keys_list = [r.key for r in paginated_keys]

    # Get details for the fetched keys
    details_query = frappe.qb.from_(t_translation).select(
        t_translation.name, t_translation.group, t_translation.key, 
        t_translation.locale, t_translation.value, t_translation.status
    ).where(t_translation.key.isin(keys_list))

    if search:
        details_query = details_query.where(
            (t_translation.key.like(f"%{search}%")) 
            | (t_translation.value.like(f"%{search}%"))
        )
    if group:
        details_query = details_query.where(t_translation.group == group)
    if locale:
        details_query = details_query.where(t_translation.locale == locale)

    details_query = details_query.orderby(t_translation.key, order=frappe.qb.asc)
    details = details_query.run(as_dict=True)

    grouped = {}
    for t in details:
        k = t['key']
        if k not in grouped:
            grouped[k] = []

        grouped[k].append({
            "id": t['name'],
            "group": t['group'],
            "locale": t['locale'],
            "value": t['value'],
            "status": t['status']
        })

    result_dict = {}
    for k in keys_list:
        if k in grouped:
            result_dict[k] = grouped[k]

    return _api_success({
        "total": total_keys,
        "perPage": per_page,
        "translations": result_dict
    })

@frappe.whitelist()
def create_translation():
    _require_admin()
    data = frappe.form_dict
    group = data.get('group')
    key = data.get('key')
    values = data.get('value')

    if isinstance(values, str):
        try:
            values = json.loads(values)
        except:
            pass

    if not group or not key or not isinstance(values, dict):
        return _api_error("Invalid parameters", 400)

    frappe.db.delete("PaaS Translation", {"key": key})

    for locale, text in values.items():
        doc = frappe.get_doc({
            "doctype": "PaaS Translation",
            "group": group,
            "key": key,
            "locale": locale,
            "value": text,
            "status": 1
        })
        doc.insert(ignore_permissions=True)

    return _api_success(message="Successfully created")

@frappe.whitelist()
def update_translation(key=None):
    _require_admin()
    data = frappe.form_dict
    target_key = key or data.get('key')

    if not target_key:
        return _api_error("Key is required", 400)

    group = data.get('group')
    values = data.get('value')

    if isinstance(values, str):
        try:
            values = json.loads(values)
        except:
            pass

    if not group or not isinstance(values, dict):
        return _api_error("Invalid parameters", 400)

    frappe.db.delete("PaaS Translation", {"key": target_key})

    for locale, text in values.items():
        doc = frappe.get_doc({
            "doctype": "PaaS Translation",
            "group": group,
            "key": target_key,
            "locale": locale,
            "value": text,
            "status": 1
        })
        doc.insert(ignore_permissions=True)

    return _api_success(message="Successfully updated")

@frappe.whitelist()
def delete_translation():
    _require_admin()
    data = frappe.form_dict
    ids = data.get('ids')

    if isinstance(ids, str):
        try:
            ids = json.loads(ids)
        except:
            pass

    if not ids or not isinstance(ids, list):
        return _api_error("Invalid parameters", 400)

    for k in ids:
        docs = frappe.get_all("PaaS Translation", filters={"key": k}, pluck="name")
        for d in docs:
            frappe.delete_doc("PaaS Translation", d, ignore_permissions=True)

    return _api_success(message="Successfully deleted")

def delete_translation_single(key):
    _require_admin()
    if not key:
        return _api_error("Key is required", 400)

    docs = frappe.get_all("PaaS Translation", filters={"key": key}, pluck="name")
    for d in docs:
        frappe.delete_doc("PaaS Translation", d, ignore_permissions=True)

    return _api_success(message="Successfully deleted")

def get_translation_single(key):
    _require_admin()
    if not key:
        return _api_error("Key is required", 400)

    docs = frappe.get_all("PaaS Translation",
                          filters={"key": key},
                          fields=["name", "group", "key", "locale", "value", "status"])

    if not docs:
        return _api_error("Translation not found", 404)

    data = []
    for t in docs:
        data.append({
            "id": t['name'],
            "group": t['group'],
            "locale": t['locale'],
            "value": t['value'],
            "status": t['status']
        })

    return _api_success(data)

@frappe.whitelist()
def drop_all_translations():
    _require_admin()
    docs = frappe.get_all("PaaS Translation", pluck="name")
    for d in docs:
        frappe.delete_doc("PaaS Translation", d, ignore_permissions=True)
    return _api_success(message="Successfully dropped all")

@frappe.whitelist()
def truncate_translations():
    _require_admin()
    frappe.db.delete("PaaS Translation")
    return _api_success(message="Successfully truncated")

@frappe.whitelist()
def restore_all_translations():
    _require_admin()
    deleted = frappe.get_all("Deleted Document", filters={"deleted_doctype": "PaaS Translation"}, pluck="name")
    from frappe.model.api import restore_document
    for d in deleted:
        try:
            restore_document(d)
        except:
            pass
    return _api_success(message="Successfully restored")

@frappe.whitelist()
def import_translations():
    _require_admin()
    try:
        import pandas as pd
        import io

        file_data = frappe.request.files.get('file')
        if not file_data:
            return _api_error("No file uploaded", 400)

        content = file_data.stream.read()
        if file_data.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            df = pd.read_csv(io.BytesIO(content))

        for index, row in df.iterrows():
            if 'key' not in row or 'locale' not in row:
                continue

            existing = frappe.get_all("PaaS Translation", filters={"key": row['key'], "locale": row['locale']}, pluck="name")
            if existing:
                doc = frappe.get_doc("PaaS Translation", existing[0])
                doc.value = row.get('value', '')
                doc.group = row.get('group', 'default')
                doc.save(ignore_permissions=True)
            else:
                frappe.get_doc({
                    "doctype": "PaaS Translation",
                    "key": row['key'],
                    "locale": row['locale'],
                    "group": row.get('group', 'default'),
                    "value": row.get('value', ''),
                    "status": 1
                }).insert(ignore_permissions=True)

        return _api_success(message="Successfully imported")

    except Exception as e:
        return _api_error(f"Import failed: {str(e)}")

@frappe.whitelist()
def export_translations():
    _require_admin()
    try:
        import pandas as pd
        from frappe.utils.file_manager import save_file
        import io

        data = frappe.get_all("PaaS Translation", fields=["group", "key", "locale", "value"])
        df = pd.DataFrame(data)

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Translations')
        writer.close()
        output.seek(0)

        fname = "translations_export.xlsx"
        saved = save_file(fname, output.getvalue(), is_private=0)

        return _api_success({
            "path": saved.file_url,
            "file_name": fname
        }, "Successfully exported")

    except Exception as e:
        try:
            output = io.StringIO()
            df.to_csv(output, index=False)
            fname = "translations_export.csv"
            saved = save_file(fname, output.getvalue().encode('utf-8'), is_private=0)
            return _api_success({
                "path": saved.file_url,
                "file_name": fname
            }, "Successfully exported (CSV)")
        except Exception as e2:
            return _api_error(f"Export failed: {str(e2)}")
