import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response
from frappe.utils import now

@frappe.whitelist()
def get_contra(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    all_vouchers = []

    journal_list = frappe.get_list('Journal Entry', filters={'company':company_name,'voucher_type':'Contra Entry'}, fields=['*'])
    for list in journal_list:
        journal_gl_entry = frappe.get_list('GL Entry', filters = {'voucher_no':list.name}, fields = ['*'])

        for entry in journal_gl_entry:
            parent_account = frappe.get_value('Account', entry['account'], 'custom_tally_parent_account')

            cr_dr = "Dr" if entry['debit_in_account_currency'] else "Cr"
            amount = entry['debit_in_account_currency'] or entry['credit_in_account_currency']

            ledger_dict = {
                "Autoid": list['name'],
                "CompanyNumber": str(company_id),
                "TallyMasterid": 1,
                "Voucherid": "",
                "VoucherNumber": list['name'],
                "VoucherDate": list['posting_date'].strftime('%d-%m-%Y'),
                "VoucherType": 'Contra',
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
                "TransactionDate": list['posting_date'].strftime('%d-%m-%Y'),
                "CrDr": cr_dr,
                "Amount": amount,
                "CostCategory": "",
                "CostCentre": entry['cost_center'].split('-')[0],
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
    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200
    

    return final_voucher


@frappe.whitelist()
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    contra_response = data.get("CONTRA RESPONSE", [])

    for response in contra_response:
        contra_entry = response.get("AUTOID")
        guid = response.get("GUID")
        ref_no = response.get("REFNO")

        if not contra_entry:
            continue

        existing_item = frappe.db.get_value("Journal Entry", {"name": contra_entry}, "name")
        if existing_item:
            frappe.db.set_value("Journal Entry", existing_item, {
                "custom_tally_auto_id": contra_entry,
                "custom_tally_guid": guid,
                "custom_tally_refno": ref_no,
                "custom_sync_time": now()
            })
            frappe.db.commit()

        else:
            frappe.log_error(f"Contra Entry not found for Tally AUTOID: {contra_entry}", "Tally Contra Entry Sync Error")
