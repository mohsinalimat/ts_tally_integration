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

    journal_list = frappe.get_all('Journal Entry',
                                   filters={'company':company_name,'voucher_type':'Journal Entry', 'custom_tally_guid': ['in', ['', None]]},
                                   fields=['*'])

    for list in journal_list:
        journal_gl_entry = frappe.get_all('GL Entry', filters = {'voucher_no':list.name}, fields = ['*'])

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




@frappe.whitelist()
def fetch_response(response):
    if not response:
        frappe.log_error("No response received from Tally", "Tally Journal Entry")
        return Response(json.dumps({"status": False, "message": "No response received"}), content_type='application/json')

    frappe.log_error(f"Raw Journal Entry Response: {response}", "Tally Journal Entry")
    
    try:
        data = json.loads(response) if isinstance(response, str) else response
    except Exception as e:
        frappe.log_error(f"JSON decode failed: {str(e)}", "Tally Journal Entry")
        return Response(json.dumps({"status": False, "message": "Invalid JSON"}), content_type='application/json')

    journal_response = data.get("JOURNAL RESPONSE", [])

    if not journal_response:
        frappe.log_error("No JOURNAL RESPONSE found in Tally response", "Tally Journal Entry")
        return Response(json.dumps({"status": False, "message": "No journal response found"}), content_type='application/json')

    for response in journal_response:
        journal_entry = response.get("AUTOID")
        guid = response.get("GUID")
        ref_no = response.get("REFNO")
        import_date = response.get("IMPORTDATE")
        import_time = response.get("IMPORTTIME")

        if not journal_entry:
            continue

        existing_journal = frappe.db.get_value("Journal Entry", {"name": journal_entry}, "name")
        if existing_journal:
            import_date = datetime.strptime(import_date, "%Y%m%d").date()
            import_time = datetime.strptime(import_time, "%H:%M:%S").time()

            frappe.db.set_value("Journal Entry", existing_journal, {
                "custom_tally_auto_id": journal_entry,
                "custom_tally_guid": guid,
                "custom_tally_refno": ref_no,
                "custom_sync_time": datetime.combine(import_date, import_time)
            })

        else:
            frappe.log_error(f"Journal Entry not found for Tally AUTOID: {journal_entry}", "Tally Journal Entry Sync Error")
    
    frappe.db.commit()
        
    return Response(json.dumps({"status": True, "message": "Updated successfully"}), content_type='application/json')
