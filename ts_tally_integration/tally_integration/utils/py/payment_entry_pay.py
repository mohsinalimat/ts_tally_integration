import frappe
import json
import requests
from datetime import datetime


@frappe.whitelist(allow_guest=True)
def get_payment_entry():
    return get_payment_entry_supplier()


def get_payment_entry_supplier():
    
    doc_list = frappe.get_all('Payment Entry', filters={'docstatus': 1, 'payment_type': 'Pay'}, fields=['*'])
    list_of_json_suppliers = []
    for doc in doc_list:
        list_of_payment_entries = []
        pay_doc = frappe.get_doc("Payment Entry", doc.name)
        supplier = frappe.get_doc("Supplier", pay_doc.party)
        supplier_add = frappe.get_doc("Address",supplier.supplier_primary_address)
        acc_doc = frappe.get_doc("Account", doc.paid_from)
        company = frappe.get_doc("Company", doc.company)
        if supplier.gst_category == "Unregistered":
            gst_category = "Unregistered/Vendor"
        elif supplier.gst_category == "Registered Regular":
            gst_category = "Regular"
        elif supplier.gst_category == "Registered Composition":
            gst_category = "Composition"
        elif supplier.gst_category == "SEZ":
            gst_category = "Regular - SEZ"
        else:
            gst_category = supplier.gst_category

        company_idx = (frappe.db.sql(f"select idx from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['idx']

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
            "BillDate": "",
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
            "Narration": doc.remarks if doc.remarks else None
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
            "LedgerParent": (acc_doc.parent_account).split(" - ")[0],
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
            "Narration": doc.remarks if doc.remarks else None
        }

        list_of_payment_entries.append(doc_dic_supplier1)

        response_supplier = {
            "status": True,
            "VOUCHERDETAILS": {
                "VOUCHER": list_of_payment_entries
            }
        }
        # list_of_json_suppliers.append(json.dumps(response_supplier))
        list_of_json_suppliers.append(response_supplier)

    return list_of_json_suppliers
