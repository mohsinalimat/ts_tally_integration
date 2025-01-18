import frappe
import json
import requests
from datetime import datetime


@frappe.whitelist(allow_guest=True)
def get_payment_entry():
    return get_payment_entry_customer()
    

def get_payment_entry_customer():
    doc_list = frappe.get_all('Payment Entry', filters={'docstatus': 1, 'payment_type': 'Receive'}, fields=['*'])
    list_of_json_customers = []
    for doc in doc_list:
        list_of_payment_entries = []
        pay_doc = frappe.get_doc("Payment Entry", doc.name)
        cust = frappe.get_doc("Customer", pay_doc.party)
        cust_add = frappe.get_doc("Address",cust.customer_primary_address)
        acc_doc = frappe.get_doc("Account", doc.paid_to)

        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(cust.gst_category, cust.gst_category)
        
        company_idx = (frappe.db.sql(f"select idx from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['idx']
        parent_account = ""
        if "cash" == acc_doc.account_type.lower():
            parent_account = "Cash-In-Hand"
        elif "bank" == acc_doc.account_type.lower():
            parent_account = "Bank Accounts"
        doc_dic_cust = {
                "Autoid": "",
                "CompanyNumber": str(company_idx),
                "TallyMasterid": 1,
                "Voucherid": doc.name,
                "VoucherNumber": doc.name,
                "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "VoucherType": "Receipt",
                "VoucherTypeParent": "Receipt",
                "LedgerName": cust.customer_name,
                "LedgerParent": "Sundry Debtors",
                "LedgerAddress": cust_add.address_line1 if cust_add.address_line1 else "",
                "LedgerState": cust_add.state if cust_add.state else "",
                "LedgerCountry": cust_add.country if cust_add.country else "",
                "LedgerPincode": cust_add.pincode if cust_add.pincode else "",
                "LedgerMobile": cust.mobile_no if cust.mobile_no else "",
                "LedgerGstReg": gst_category if gst_category else "",
                "LedgerGstin": cust.gstin if cust.gstin else "",
                "LedgerPan": cust.pan if cust.pan else None,
                "BillName": "",
                "BillDate": "",
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
                "Autoid": "",
                "CompanyNumber": str(company_idx),
                "TallyMasterid": 1,
                "Voucherid": doc.name,
                "VoucherNumber": doc.name,
                "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "VoucherType": "Receipt",
                "VoucherTypeParent": "Receipt",
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
                "BillDate": "",
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
            
        response_cust = {
                "status": True,
                "VOUCHERDETAILS": {
                    "VOUCHER": list_of_payment_entries
                }
            }

        # list_of_json_customers.append(json.dumps(response_cust))
        list_of_json_customers.append(response_cust)

    return list_of_json_customers

