import frappe
from frappe.core.doctype.user.user import generate_keys
from frappe.utils import get_url
from frappe.permissions import add_permission

def user_creation():

    if frappe.db.exists("User", "tally@thirvusoft.co.in"):
        return
    role_creation()
    user = frappe.new_doc("User")
    user.email = "tally@thirvusoft.co.in"
    user.first_name = "Tally"
    user.last_name = "User"
    user.send_welcome_email = 0
    user.username = "tallyuser"
    user.add_roles("Tally User")
    user.save()
    api_generate_secret = generate_keys("tally@thirvusoft.co.in")

    secret_key = api_generate_secret["api_secret"]
    api_key = frappe.db.get_value("User", "tally@thirvusoft.co.in", "api_key")

    base_url = get_url()
    api_details = f'''API Key: {api_key}\n\nSecret Key: {secret_key}\n\nPurchase Invoice(Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.purchase_invoice_inventory.get_purchase_invoice\n\nPurchase Invoice(Non-Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.purchase_invoice_non_inventory.get_purchase_invoice\n\nDebit Note(Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.debit_note_inventory.get_debit_note\n\nDebit Note(Non-Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.debit_note_non_inventory.get_debit_note\n\nSales Invoice(Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.sales_inv.get_sales\n\nSales Invoice (Non-Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.sales_noninv.get_sales\n\nCredit Note(Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.credit_inv.credit_note\n\nCredit Note(Non-Inventory): {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.credit_noninv.credit_note\n\n'''

    frappe.db.set_value("TS Tally Settings", "TS Tally Settings", "api_details", api_details)

    tally_settings = frappe.get_doc("TS Tally Settings", "TS Tally Settings")
    tally_settings.reload()


def role_creation():
    if frappe.db.exists("Role", "Tally User"):
        return
    role = frappe.new_doc("Role")
    role.role_name = "Tally User"
    role.desk_access = 1
    role.save()
    role_permission(role.role_name)

def role_permission(role_name):
    doctypes = ["Sales Invoice", "Purchase Invoice", "Delivery Note", "Purchase Receipt", "Stock Entry"]

    for doctype in doctypes:
        existing_permission = frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role_name})
        
        if not existing_permission:
            add_permission(doctype, role_name, 0, "read")