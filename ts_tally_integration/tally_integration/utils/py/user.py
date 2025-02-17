import frappe
from frappe.core.doctype.user.user import generate_keys
from frappe.utils import get_url

def user_creation():
    if frappe.db.exists("User", "tallyuser@example.com"):
        return
    role_creation()
    user = frappe.new_doc("User")
    user.email = "tallyuser@example.com"
    user.first_name = "Tally"
    user.last_name = "User"
    user.send_welcome_email = 0
    user.username = "tallyuser"
    user.add_roles("Tally User")
    user.save()
    api_generate_secret = generate_keys("tallyuser@example.com")

    secret_key = api_generate_secret["api_secret"]
    api_key = frappe.db.get_value("User", "tallyuser@example.com", "api_key")
    
    base_url = get_url()
    
    api_details = f'''
    API Keys: {api_key}\n\n
    Secret Key: {secret_key}\n\n
    Purchase Invoice: {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.purchase_invoice_inventory.get_purchase_invoice\n\n
    Debit Note: {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.debit_note_inventory.get_debit_note\n\n
    Sales Invoice Non Inventory: {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.sales_noninv.get_sales\n\n
    Sales Invoice Inventory: {base_url}/api/method/ts_tally_integration.tally_integration.utils.api.sales_inv.get_sales

    '''
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
    for doctype in ["Sales Invoice", "Purchase Invoice"]:
        if frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role_name}):
            continue
        role_permission = frappe.new_doc("Custom DocPerm")
        role_permission.parent = doctype
        role_permission.role = role_name
        role_permission.permlevel = 0
        role_permission.read = 1
        role_permission.export = 0
        role_permission.save()
