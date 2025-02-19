import frappe
from datetime import datetime
import json
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_stock_entry():

    stock_entry = frappe.db.get_all('Stock Entry',filters={'stock_entry_type':'Material Transfer','name':'DN-25-00003','is_return':0,'docstatus':1},fields=['*'])
    company_idx = (frappe.db.sql(f"select company_number from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['company_number']
    
    all_vouchers = []
    final_voucher = []
    for doc in stock_entry:

        ledger_dict ={
            "Autoid": "2",
            "CompanyNumber": company_idx,
            "TallyMasterid": "1",
            "Voucherid": "",
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType": "StockJournal",
            "VoucherTypeParent": "StockJournal",
            "LedgerName": "",
            "LedgerParent": "",
            "LedgerAddress": "",
            "LedgerState": "",
            "LedgerCountry": "",
            "LedgerPincode": "",
            "LedgerMobile": "",
            "LedgerGstReg": "",
            "LedgerGstin": "",
            "BillName": "",
            "BillDate": "",
            "CrDr": "Dr",
            "CostCategory": "",
            "CostCentre": "",
            "Stockitem": "24KT BULLION GOLD",
            "Godown": "1",
            "BatchNo": "Primary Batch",
            "Quantity": "411.893",
            "Rate": "4820",
            "Discount": "",
            "Amount": "1985324",
            "BuyerName": "",
            "BuyerMailingName": "",
            "BuyerAddress1": "",
            "BuyerAddress2": "",
            "BuyerState": "",
            "BuyerCountry": "",
            "ConsigneeName": "",
            "ConsigneeMailingName": "",
            "ConsigneeAddress1": "",
            "ConsigneeAddress2": "",
            "ConsigneeState": "",
            "ConsigneeCountry": "",
            "Narration": "null",
            "Void": "in"
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

