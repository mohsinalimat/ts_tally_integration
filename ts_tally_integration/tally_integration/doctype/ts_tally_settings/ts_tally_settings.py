# Copyright (c) 2024, Siddarth and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.core.doctype.user.user import generate_keys
from frappe.utils import get_url
from frappe.permissions import add_permission


class TSTallySettings(Document):
	pass

@frappe.whitelist()
def get_unmapped_accounts():
	unmapped_account = frappe.db.get_list('Account', filters={'custom_tally_parent_account':['=',''], 'is_group':0}, fields=['name', 'company'])
	return unmapped_account


def user_creation(user_id):

    if frappe.db.exists("User",user_id):
        return
    user = frappe.new_doc("User")
    user.email = user_id
    user.first_name = "Tally"
    user.last_name = "User"
    user.send_welcome_email = 0
    user.username = "tallyuser"
    user.add_roles("Tally User")
    user.save()
    api_generate_secret = generate_keys(user_id)

    secret_key = api_generate_secret["api_secret"]
    api_key = frappe.db.get_value("User", user_id, "api_key")

    base_url = get_url()

    item_master = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.item.get_purchase_invoice" # Item
    item_group = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.item_group.get_purchase_invoice" # Itemgroup
    warehouse = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.warehouse.get_purchase_invoice" # Warehouse
    party = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.party.get_purchase_invoice" # Party


    purchase_invoice_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.purchase_invoice_inventory.get_purchase_invoice" # Purchase Invoice (Inventory)
    purchase_invoice_non_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.purchase_invoice_non_inventory.get_purchase_invoice" # Purchase Invoice (Non-Inventory)

    debit_note_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.debit_note_inventory.get_debit_note" # Purchase Invoice (Return)
    debit_note_non_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.debit_note_non_inventory.get_debit_note" # Purchase Invoice Return (Non-Inventory) 

    payment_entry_pay = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.payment_entry_pay.get_payment_entry" # Payment Entry type (Pay)
    payment_entry_receipt = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.payment_entry_receipt.get_payment_entry" # Payment Entry type (Receive)

    sales_invoice_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.sales_invoice_inventory.get_sales_inv" # Sales Invocie (Inventory)
    sales_invoice_non_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.sales_invoice_non_inventory.get_sales_non_inv" # Sales Invocie (Non-Inventory)

    credit_note_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.credit_note_inventory.credit_note_inv" # Credit Note (Inventory)
    credit_note_non_inventory = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.credit_note_non_inventory.credit_note_non_inv"  # Credit Note (Non-Inventory)

    journal_entry = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.journal_entry.get_journal"  # journal Entry
    contra_entry = f"{base_url}/api/method/ts_tally_integration.tally_integration.utils.api.contra_entry.get_contra" # Contra Entry

    api_details = f'''API Key: {api_key}

    Secret Key: {secret_key}

    Item Master: {item_master}

    Item Group: {item_group}

    Warehouse: {warehouse}

    Party: {party}

    Purchase Invoice (Inventory): {purchase_invoice_inventory}

    Purchase Invoice (Non-Inventory): {purchase_invoice_non_inventory}

    Debit Note (Inventory): {debit_note_inventory}

    Debit Note (Non-Inventory): {debit_note_non_inventory}

    Sales Invoice (Inventory): {sales_invoice_inventory}

    Sales Invoice (Non-Inventory): {sales_invoice_non_inventory}

    Credit Note (Inventory): {credit_note_inventory}

    Credit Note (Non-Inventory): {credit_note_non_inventory}

    Journal Entry: {journal_entry}

    Contra Entry: {contra_entry}

    Payment Entry (Pay): {payment_entry_pay}

    Payment Entry (Receipt): {payment_entry_receipt}'''

    frappe.db.set_value("TS Tally Settings", "TS Tally Settings", "api_details", api_details)


def role_creation(role_name):
    if frappe.db.exists("Role", role_name):
        return
    role = frappe.new_doc("Role")
    role.role_name = role_name
    role.desk_access = 0
    role.save()


def role_permission(role_name):
    doctypes = ["GL Entry","Journal Entry","Address","Customer","Account","Sales Invoice", "Purchase Invoice", "Delivery Note", "Purchase Receipt", "Stock Entry", "Payment Entry", "Company", "Account", "Supplier", "Customer"]
    
    for doctype in doctypes:
        existing_permission = frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role_name})
        
        if not existing_permission:
            add_permission(doctype, role_name, 0, "read")
