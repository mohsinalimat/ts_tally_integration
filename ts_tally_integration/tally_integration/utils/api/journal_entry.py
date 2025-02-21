import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist()
def get_journal(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    all_vouchers = []

    journal_list = frappe.get_list('Journal Entry', filters={'company':company_name,'voucher_type':'Journal Entry'}, fields=['*'])
    for list in journal_list:
        journal_gl_entry = frappe.get_list('GL Entry', filters = {'voucher_no':list.name}, fields = ['*'])

        for entry in journal_gl_entry:
            parent_account = frappe.get_value('Account', entry['account'], 'custom_tally_parent_account')

            cr_dr = "Dr" if entry['debit_in_account_currency'] else "Cr"
            amount = entry['debit_in_account_currency'] or entry['credit_in_account_currency']

            ledger_dict = {
                "Autoid": "1",
                "CompanyNumber": str(company_id),
                "TallyMasterid": 1,
                "Voucherid": "",
                "VoucherNumber": list['name'],
                "VoucherDate": list['posting_date'].strftime('%d-%m-%Y'),
                "VoucherType": 'Journal',
                "VoucherTypeParent": "Journal",
                "LedgerName": (entry['account']).split(" - ")[0],
                "LedgerParent": parent_account,
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
                "TransactionDate": list['posting_date'].strftime('%d-%m-%Y'),
                "CrDr": cr_dr,
                "Amount": amount,
                "CostCategory1": "",
                "CostCentre1": entry['cost_center'].split('-')[0],
                "CostCategory2": "",
                "CostCentre2": "",
                "CostCategory3": "",
                "CostCentre3": "",				
                "CostCategory4": "",
                "CostCentre4": "",
                "CostCategory5": "",
                "CostCentre5": "",				
                "BranchCode": "",
                "Location": "",
                "State": "",
                "Narration": None
            }
            all_vouchers.append(ledger_dict)

    final_voucher = ({
        "status": True,
        "VOUCHERDETAILS": {
            "VOUCHER": all_vouchers
        }
    })

    final_voucher = final_voucher
    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200

    return final_voucher
