import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_journal():
    journal_doc = frappe.db.get_all('Journal Entry',filters={'voucher_type':'Journal Entry'},fields=['*'])

    all_vouchers = []

    for doc in journal_doc:
        link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': doc['company']}, fields=['parent'])

        company_idx = (frappe.db.sql(f"select company_number from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['company_number']

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
                "Autoid": "1",
                "CompanyNumber": str(company_idx),
                "TallyMasterid": 1,
                "Voucherid": "",
                "VoucherNumber": doc['name'],
                "VoucherDate": doc['posting_date'].strftime('%d-%m-%Y'),
                "VoucherType": 'Journal',
                "VoucherTypeParent": "Journal",
                "LedgerName": (entry['account']).split(" - ")[0],
                "LedgerParent": parent_acc,
                "LedgerAddress": "",
                "LedgerState": "",
                "LedgerCountry": "",
                "LedgerPincode": "",
                "LedgerMobile": "",
                "LedgerGstReg": "",
                "LedgerGstin": "",
    	        "LedgerPan": 'null',
                "BillName": "",
                "BillDate": "",
                "PlaceOfSupply": "",
                "TransactionDate": doc['posting_date'].strftime('%d-%m-%Y'),
                "CrDr": cr_dr,
                "Amount": amount,
                "CostCategory1": "",
                "CostCentre1": entry['cost_center'],
                "CostCategory2": "",
                "CostCentre2": "",
                "CostCategory3": "",
                "CostCentre3": "",				
                "CostCategory4": "",
                "CostCentre4": "",
                "CostCategory5": "",
                "CostCentre5": "",				
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

    all_vouchers = all_vouchers[0]    
    all_vouchers = Response(json.dumps(all_vouchers, default=str), content_type='application/json')
    all_vouchers.status_code = 200
 
    return all_vouchers
