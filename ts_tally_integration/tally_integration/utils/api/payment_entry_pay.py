import frappe
import json
import requests
from datetime import datetime
from werkzeug.wrappers import Response
from itertools import chain


@frappe.whitelist()
def get_payment_entry(company=None):
    return get_payment_entry_supplier(company)


def get_payment_entry_supplier(company):
    if company==None:
        return Response(json.dumps("Company Number is not found!", default=str), content_type='application/json', status=404)

    company_list = frappe.db.sql("select company_name from `tabTS Tally Company` where company_number=%s", company, as_dict=1)
    
    if len(company_list)==0:
        return Response(json.dumps("Company is not found. Please check the company number!", default=str), content_type='application/json', status=404)

    company_name = company_list[0].company_name
    
    doc_list = frappe.db.get_list('Payment Entry', filters={'docstatus': 1, "company" : company_name, 'payment_type': 'Pay'}, fields=['*'])
    list_of_json_suppliers = []
    list_of_payment_entries = []

    for doc in doc_list:
        pay_doc = frappe.get_doc("Payment Entry", doc.name)
        supplier = frappe.get_doc("Supplier", pay_doc.party)
        supplier_add = frappe.get_doc("Address",supplier.supplier_primary_address)
        acc_doc = frappe.get_doc("Account", doc.paid_from)
        company = frappe.get_doc("Company", doc.company)
        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(supplier.gst_category, supplier.gst_category)

        company_idx = (frappe.db.sql(f"select company_number from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['company_number']
        parent_account = ""
        if "cash" == acc_doc.account_type.lower():
            parent_account = "Cash-In-Hand"
        elif "bank" == acc_doc.account_type.lower():
            parent_account = "Bank Accounts"
        
        doc_dic_supplier = {
            "Autoid": "",
            "CompanyNumber": str(company_idx),
            "TallyMasterid": 1,
            "Voucherid": doc.name,
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType":"Payment",
            "VoucherTypeParent": "Payment",
            "LedgerName": supplier.supplier_name,
            "LedgerParent": "Sundry Creditors",
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
            "CompanyNumber": str(company_idx),
            "TallyMasterid": 1,
            "Voucherid": doc.name,
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType": "Payment",
            "VoucherTypeParent": "Payment",
            "LedgerName": (acc_doc.name).split(" - ")[0],
            "LedgerParent":parent_account if parent_account!="" else (acc_doc.parent_account).split(" - ")[0],
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

    # response_supplier = {
    #     "status": True,
    #     "VOUCHERDETAILS": {
    #         "VOUCHER": list_of_payment_entries
    #     }
    # }
    # list_of_json_suppliers.append(json.dumps(response_supplier))
    list_of_json_suppliers.append(list_of_payment_entries)

    flattened_list = list(chain.from_iterable(list_of_json_suppliers))

    response_payment = {
        "status": True,
        "VOUCHERDETAILS": {
            "VOUCHER": flattened_list
        }
    }

    return Response(json.dumps(response_payment, default=str), content_type='application/json', status=200)