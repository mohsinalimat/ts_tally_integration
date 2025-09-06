import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response
from itertools import chain


@frappe.whitelist(allow_guest=True)
def get_payment_entry(company_id=None):

    if company_id == None:
        return Response(json.dumps("Company ID is not found!", default=str), content_type='application/json', status=404)

    company_name = frappe.get_value("TS Tally Company", {"company_number" : company_id}, fieldname="company_name")
    
    if company_name==None:
        return Response(json.dumps("Company is not found. Please check the company id!", default=str), content_type='application/json', status=404)

    doc_list = frappe.get_list('Payment Entry',
                               filters={'docstatus': 1, "company" : company_name, 'payment_type': 'Receive', 'custom_tally_guid': ['is', 'not set']},
                               fields=['*'])

    list_of_json_customers = []
    list_of_payment_entries = []

    for doc in doc_list:

        cust = frappe.get_doc("Customer", doc.party)
        if cust.customer_primary_address:
            cust_add = frappe.get_doc("Address",cust.customer_primary_address)
        acc_doc_paid_from = frappe.get_doc("Account", doc.paid_from)
        acc_doc_paid_to = frappe.get_doc("Account", doc.paid_to)

        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(cust.gst_category, cust.gst_category)

        doc_dic_cust = {
                "Autoid": doc.name,
                "CompanyNumber": str(company_id),
                "TallyMasterid": 1,
                "Voucherid": doc.name,
                "VoucherNumber": doc.name,
                "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "VoucherType": "Receipt",
                "VoucherTypeParent": "Receipt",
                "LedgerName": cust.customer_name,
                "LedgerParent": (acc_doc_paid_from.custom_tally_parent_account) if acc_doc_paid_from.custom_tally_parent_account else "",
                "LedgerAddress": cust_add.address_line1 if cust_add.address_line1 else "",
                "LedgerState": cust_add.state if cust_add.state else "",
                "LedgerCountry": cust_add.country if cust_add.country else "",
                "LedgerPincode": cust_add.pincode if cust_add.pincode else "",
                "LedgerMobile": cust.mobile_no if cust.mobile_no else "",
                "LedgerGstReg": gst_category if gst_category else "",
                "LedgerGstin": cust.gstin if cust.gstin else "",
                "LedgerPan": cust.pan if cust.pan else None,
                "BillName": "",
                "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "PlaceOfSupply": doc.place_of_supply if doc.place_of_supply else "",
                "TransactionDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "CrDr": "Cr",
                "Amount": str(doc.paid_amount),
                "CostCategory1": "",
                "CostCentre1": doc.cost_center.split(" - ")[0] if doc.cost_center else "",
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
                "Narration": doc.remarks.replace("\n", ". ") if doc.remarks else None
            }

        list_of_payment_entries.append(doc_dic_cust)

        doc_dic_cust1 = {
                "Autoid": doc.name,
                "CompanyNumber": str(company_id),
                "TallyMasterid": 1,
                "Voucherid": doc.name,
                "VoucherNumber": doc.name,
                "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "VoucherType": "Receipt",
                "VoucherTypeParent": "Receipt",
                "LedgerName": (acc_doc_paid_to.name).split(" - ")[0],
                "LedgerParent": (acc_doc_paid_to.custom_tally_parent_account) if acc_doc_paid_to.custom_tally_parent_account else "",
                "LedgerAddress": "",
                "LedgerState": "",
                "LedgerCountry": "",
                "LedgerPincode": "",
                "LedgerMobile": "",
                "LedgerGstReg": "",
                "LedgerGstin": "",
                "LedgerPan": None,				
                "BillName": "",
                "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "PlaceOfSupply": "",
                "TransactionDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "CrDr": "Dr",
                "Amount": str(doc.paid_amount),
                "CostCategory1": "",
                "CostCentre1": doc.cost_center.split(" - ")[0] if doc.cost_center else "",
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
                "Narration": doc.remarks.replace("\n", ". ") if doc.remarks else None
            }

        list_of_payment_entries.append(doc_dic_cust1)
            
    list_of_json_customers.append(list_of_payment_entries)

    response_payment = {
        "status": True,
        "VOUCHERDETAILS": {
            "VOUCHER": list(chain.from_iterable(list_of_json_customers))
        }
    }
    
    return Response(json.dumps(response_payment, default=str), content_type='application/json', status=200)




@frappe.whitelist(allow_guest=True)
def fetch_response(response):
    if not response:
        frappe.log_error("No response received from Tally", "Tally Payment Entry")
        return Response(json.dumps({"status": False, "message": "No response received"}), content_type='application/json')

    frappe.log_error(f"Raw Payment Entry Response: {response}", "Tally Payment Entry")

    try:
        data = json.loads(response) if isinstance(response, str) else response
    except Exception as e:
        frappe.log_error(f"JSON decode failed: {str(e)}", "Tally Payment Entry")
        return Response(json.dumps({"status": False, "message": "Invalid JSON"}), content_type='application/json')

    payment_response = data.get("RECEIPT RESPONSE", [])

    if not payment_response:
        frappe.log_error("No PAYMENT RESPONSE found in Tally response", "Tally Payment Entry")
        return Response(json.dumps({"status": False, "message": "No payment response found"}), content_type='application/json')

    for response in payment_response:
        payment_entry = response.get("AUTOID")
        guid = response.get("GUID")
        ref_no = response.get("REFNO")
        import_date = response.get("IMPORTDATE")
        import_time = response.get("IMPORTTIME")

        if not payment_entry:
            continue

        existing_payment = frappe.db.get_value("Payment Entry", {"name": payment_entry}, "name")
        if existing_payment:
            try:
                import_date = datetime.strptime(import_date, "%Y%m%d").date()
                import_time = datetime.strptime(import_time, "%H:%M:%S").time()

                frappe.db.set_value("Payment Entry", existing_payment, {
                    "custom_tally_auto_id": payment_entry,
                    "custom_tally_guid": guid,
                    "custom_tally_refno": ref_no,
                    "custom_sync_time": datetime.combine(import_date, import_time)
                })
            except Exception as e:
                frappe.log_error(f"Failed to update Payment Entry {payment_entry}: {str(e)}", "Tally Payment Entry Update Error")
        else:
            frappe.log_error(f"Payment Entry not found for Tally AUTOID: {payment_entry}", "Tally Payment Entry Sync Error")

    frappe.db.commit()

    return Response(json.dumps({
        "status": True,
        "message": f"Updated successfully"
    }), content_type='application/json')

