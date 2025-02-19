import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist()
def get_contra(company=None):
    if company==None:
        return "Company Number not found!"
    company_number = frappe.db.exists('TS Tally Company', {'company_number': company})
    if company_number:
        tally_settings = frappe.db.get_all('TS Tally Company', filters={'name': company_number}, fields=['*'])
        company_name = tally_settings[0]['company_name']

        journal_doc = frappe.db.get_list('Journal Entry',filters={'company':company_name,'voucher_type':'Contra Entry'},fields=['*'])
    
        all_vouchers = []
        final_voucher = []

        for doc in journal_doc:
            address_link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': doc['company']}, fields=['parent'])

            company_idx_number = (frappe.db.sql(f"select company_number from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['company_number']

            address = frappe.db.get_list('Address',filters={'name': address_link[0]['parent']} if address_link else {}, fields=['gst_state', 'city'])
            journal_gl_entry = frappe.db.get_list('GL Entry', filters = {'voucher_no':doc.name}, fields = ['*'])


            for entry in journal_gl_entry:
                parent_account = frappe.db.get_value('Account', entry['account'], 'custom_tally_parent_account')

                cr_dr = "Dr" if entry['debit_in_account_currency'] else "Cr"
                amount = entry['debit_in_account_currency'] or entry['credit_in_account_currency']

                ledger_dict = {
                    "Autoid": "1",
                    "CompanyNumber": str(company_idx_number),
                    "TallyMasterid": 1,
                    "Voucherid": "",
                    "VoucherNumber": doc['name'],
                    "VoucherDate": doc['posting_date'].strftime('%d-%m-%Y'),
                    "VoucherType": doc['voucher_type'],
                    "VoucherTypeParent": "Contra",
                    "LedgerName": (entry['account']).split(" - ")[0],
                    "LedgerParent": parent_account,
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
                    "TransactionDate": doc['posting_date'].strftime('%d-%m-%Y'),
                    "CrDr": cr_dr,
                    "Amount": amount,
                    "CostCategory": "",
                    "CostCentre": entry['cost_center'],
                    "BranchCode": "",
                    "Location": address[0]['city'] if address else "",
                    "State": address[0]['gst_state'] if address else "",
                    "Narration": None
                }
                all_vouchers.append(ledger_dict)

        final_voucher.append({
            "status": True,
            "VOUCHERDETAILS": {
                "VOUCHER": all_vouchers
            }
        })

        final_voucher = final_voucher[0]
        final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
        final_voucher.status_code = 200
        

        return final_voucher
