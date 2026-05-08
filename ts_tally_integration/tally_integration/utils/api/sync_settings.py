import frappe
from frappe.utils import cint


def get_master_sync_limit(default=10):
    return _get_settings_limit("master_limit", default)


def get_voucher_sync_limit(default=10):
    return _get_settings_limit("voucher_limit", default)


def _get_settings_limit(fieldname, default):
    sync_limit = frappe.db.get_single_value("TS Tally Settings", fieldname)
    if sync_limit is None:
        return default

    return cint(sync_limit)
