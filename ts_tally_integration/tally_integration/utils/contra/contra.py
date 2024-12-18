import frappe
import json
from datetime import datetime


@frappe.whitelist(allow_guest = True)
def get_contra():
    journal_doc = frappe.db.get_all('Journal Entry',filters={'name': 'ACC-JV-2024-00001'},fields=['*'])
    
    all_vouchers = []

    for doc in journal_doc:
        link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': doc['company']}, fields=['parent'])
        company_num = frappe.db.get_value('Company', {'name': doc['company']}, 'idx')
        address = frappe.db.get_all('Address',filters={'name': link[0]['parent']} if link else {}, fields=['gst_state', 'city'])
        journal_child = frappe.db.get_all('GL Entry', filters = {'voucher_no':doc.name}, fields = ['*'])

        vouchers = []

        for entry in journal_child:
            account_type = frappe.db.get_value('Account', entry['account'], 'account_type')
            if account_type == 'Cash':
                parent_acc = "Cash-in-Hand"
            elif account_type == 'Bank':
                parent_acc = "Bank Accounts"

            cr_dr = "Dr" if entry['debit_in_account_currency'] else "Cr"
            amount = entry['debit_in_account_currency'] or entry['credit_in_account_currency']

            ledger_entry = {
                "Autoid": "13259",
                "CompanyNumber": company_num,
                "TallyMasterid": 1,
                "Voucherid": "",
                "VoucherNumber": doc['name'],
                "VoucherDate": doc['posting_date'].strftime('%Y%m%d'),
                "VoucherType": doc['voucher_type'],
                "VoucherTypeParent": "Contra",
                "LedgerName": entry['account'],
                "LedgerParent": parent_acc,
                "LedgerAddress": "",
                "LedgerState": "",
                "LedgerCountry": "",
                "LedgerPincode": "",
                "LedgerMobile": "",
                "LedgerGstReg": "",
                "LedgerGstin": "",
                "LedgerPan": None,
                "BillName": "",
                "BillDate": "",
                "PlaceOfSupply": "",
                "TransactionDate": doc['posting_date'].strftime('%Y%m%d'),
                "CrDr": cr_dr,
                "Amount": amount,
                "CostCategory": "",
                "CostCentre": entry['cost_center'],
                "BranchCode": "",
                "Location": address[0]['city'] if address else "",
                "State": address[0]['gst_state'] if address else "",
                "Narration": None
            }
            vouchers.append(ledger_entry)

        all_vouchers.append({
            "status": True,
            "VOUCHERDETAILS": {
                "VOUCHER": vouchers
            }
        })

    return all_vouchers
