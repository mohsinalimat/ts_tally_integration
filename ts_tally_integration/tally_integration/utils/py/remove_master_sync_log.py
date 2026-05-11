import frappe
from frappe import _


ALLOWED_DOCTYPES = {
    "Customer",
    "Supplier",
    "Item",
    "Account",
    "Item Group",
    "Warehouse",
}

CHILD_DOCTYPE = "Tally Master Sync Log"
PARENTFIELD = "custom_tally_sync_log"


def _ensure_administrator():
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only Administrator can remove Tally sync log"), frappe.PermissionError)


def _validate_doctype(doctype):
    if doctype not in ALLOWED_DOCTYPES:
        frappe.throw(_("Remove Tally Sync Log is not supported for {0}").format(doctype))


def _clear_sync_log_for_record(doctype, name, company):
    frappe.db.delete(
        CHILD_DOCTYPE,
        {
            "parenttype": doctype,
            "parentfield": PARENTFIELD,
            "parent": name,
            "company_name": company,
        },
    )


@frappe.whitelist()
def bulk_remove_master_sync_log(doctype, names, company):
    _ensure_administrator()
    _validate_doctype(doctype)

    if isinstance(names, str):
        names = frappe.parse_json(names)

    if not names:
        frappe.throw(_("No records selected"))

    if not company:
        frappe.throw(_("Company is required"))

    if not frappe.db.exists("Company", company):
        frappe.throw(_("Company {0} does not exist").format(company))

    cleared = []
    failed = []
    for name in names:
        try:
            _clear_sync_log_for_record(doctype, name, company)
            cleared.append(name)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Tally Remove Master Sync Log failed for {doctype} {name}",
            )
            failed.append(name)

    frappe.db.commit()
    return {"cleared": cleared, "failed": failed}
