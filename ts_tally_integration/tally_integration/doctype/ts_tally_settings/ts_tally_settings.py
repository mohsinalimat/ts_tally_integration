# Copyright (c) 2024, Siddarth and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TSTallySettings(Document):
	pass

@frappe.whitelist()
def get_unmapped_accounts():
	unmapped_account = frappe.db.get_list('Account', filters={'custom_tally_parent_account':['=',''], 'is_group':0}, fields=['name', 'company'])
	return unmapped_account

