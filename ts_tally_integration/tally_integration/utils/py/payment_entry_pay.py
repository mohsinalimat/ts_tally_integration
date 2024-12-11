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
        doc_dic_supplier = {
            "Autoid": "",
            "CompanyNumber": doc.company,
            "TallyMasterid": 1,
            "Voucherid": doc.name,
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType":doc.payment_type,
            "VoucherTypeParent": "Payment",
            "LedgerName": supplier.supplier_name,
            "LedgerParent": "Sundry Creditors",
            "LedgerAddress": supplier_add.address_line1 if supplier_add.address_line1 else "",
            "LedgerState": supplier_add.state if supplier_add.state else "",
            "LedgerCountry": supplier_add.country if supplier_add.country else "", 
            "LedgerPincode": supplier_add.pincode if supplier_add.pincode else "",
            "LedgerMobile": supplier.mobile_no if supplier.mobile_no else "",
            "LedgerGstReg": supplier.gst_category if supplier.gst_category else "",
            "LedgerGstin": supplier.gstin if supplier.gstin else "",
            "LedgerPan": supplier.pan if supplier.pan else None,
            "BillName": "",
            "BillDate": "",
            "PlaceOfSupply": "",
            "TransactionDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "CrDr": "Dr",
            "Amount": str(doc.paid_amount),
            "CostCategory1": "",
            "CostCentre1": doc.cost_center if doc.cost_center else '',
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
            "CompanyNumber": doc.company,
            "TallyMasterid": 1,
            "Voucherid": doc.name,
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType": doc.payment_type,
            "VoucherTypeParent": "Payment",
            "LedgerName": doc.mode_of_payment,
            "LedgerParent": doc.paid_from,
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
            "CostCentre1": doc.cost_center if doc.cost_center else "",
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
