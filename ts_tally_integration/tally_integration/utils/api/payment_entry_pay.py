import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response
from itertools import chain


@frappe.whitelist()
def get_payment_entry(company_id=None):

    if company_id == None:
        return Response(json.dumps("Company ID is not found!", default=str), content_type='application/json', status=404)

    tally_company_table = frappe.get_value("TS Tally Company", {"company_number" : company_id}, ["company_name"], as_dict=1)
    
    if tally_company_table.company_name==None:
        return Response(json.dumps("Company is not found. Please check the company id!", default=str), content_type='application/json', status=404)
  
    doc_list = frappe.get_list('Payment Entry', filters={'docstatus': 1, "company" : tally_company_table.company_name, 'payment_type': 'Pay'}, fields=['*'])
    list_of_json_suppliers = []
    list_of_payment_entries = []

    for doc in doc_list:
        supplier = frappe.get_doc("Supplier", doc.party)
        supplier_add = frappe.get_doc("Address",supplier.supplier_primary_address)
        acc_doc_paid_from = frappe.get_doc("Account", doc.paid_from)
        acc_doc_paid_to = frappe.get_doc("Account", doc.paid_to)

        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(supplier.gst_category, supplier.gst_category)

        doc_dic_supplier = {
            "Autoid": "",
            "CompanyNumber": str(company_id),
            "TallyMasterid": 1,
            "Voucherid": doc.name,
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType":"Payment",
            "VoucherTypeParent": "Payment",
            "LedgerName": supplier.supplier_name,
            "LedgerParent": (acc_doc_paid_to.custom_tally_parent_account) if acc_doc_paid_to.custom_tally_parent_account else "",
            "LedgerAddress": supplier_add.address_line1 if supplier_add.address_line1 else "",
            "LedgerState": supplier_add.state if supplier_add.state else "",
            "LedgerCountry": supplier_add.country if supplier_add.country else "", 
            "LedgerPincode": supplier_add.pincode if supplier_add.pincode else "",
            "LedgerMobile": supplier.mobile_no if supplier.mobile_no else "",
            "LedgerGstReg": gst_category if gst_category else "",
            "LedgerGstin": supplier.gstin if supplier.gstin else "",
            "LedgerPan": supplier.pan if supplier.pan else None,
            "BillName": "",
            "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "PlaceOfSupply": doc.place_of_supply if doc.place_of_supply else "",
            "TransactionDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "CrDr": "Dr",
            "Amount": str(doc.paid_amount),
            "CostCategory1": "",
            "CostCentre1": doc.cost_center.split(" - ")[0] if doc.cost_center else "",
            "CostCategory2": "",
            "CostCentre2": "" ,
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

        list_of_payment_entries.append(doc_dic_supplier)

        doc_dic_supplier1 = {
            "Autoid": "",
            "CompanyNumber": str(company_id),
            "TallyMasterid": 1,
            "Voucherid": doc.name,
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType": "Payment",
            "VoucherTypeParent": "Payment",
            "LedgerName": (acc_doc_paid_from.name).split(" - ")[0],
            "LedgerParent": (acc_doc_paid_from.custom_tally_parent_account) if acc_doc_paid_from.custom_tally_parent_account else "",
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

        list_of_payment_entries.append(doc_dic_supplier1)

    list_of_json_suppliers.append(list_of_payment_entries)
   
    response_payment = {
        "status": True,
        "VOUCHERDETAILS": {
            "VOUCHER": list(chain.from_iterable(list_of_json_suppliers))
        }
    }

    return Response(json.dumps(response_payment, default=str), content_type='application/json', status=200)