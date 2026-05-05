import frappe
from frappe import _


ALLOWED_DOCTYPES = {
    "Sales Invoice",
    "Purchase Invoice",
    "Journal Entry",
    "Payment Entry",
}

SYNC_FIELDS = (
    "custom_tally_auto_id",
    "custom_tally_refno",
    "custom_tally_guid",
    "custom_sync_time",
)


def _ensure_administrator():
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only Administrator can remove Tally sync data"), frappe.PermissionError)


def _clear_sync_fields(doctype, name):
    if doctype not in ALLOWED_DOCTYPES:
        frappe.throw(_("Remove Sync Data is not supported for {0}").format(doctype))

    updates = {field: None for field in SYNC_FIELDS}
    frappe.db.set_value(doctype, name, updates, update_modified=False)


@frappe.whitelist()
def remove_sync_data(doctype, name):
    _ensure_administrator()
    _clear_sync_fields(doctype, name)
    frappe.db.commit()
    return {"status": "success", "name": name}


@frappe.whitelist()
def bulk_remove_sync_data(doctype, names):
    _ensure_administrator()

    if isinstance(names, str):
        names = frappe.parse_json(names)

    if not names:
        frappe.throw(_("No records selected"))

    cleared = []
    failed = []
    for name in names:
        try:
            _clear_sync_fields(doctype, name)
            cleared.append(name)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Tally Remove Sync Data failed for {doctype} {name}")
            failed.append(name)

    frappe.db.commit()
    return {"cleared": cleared, "failed": failed}
