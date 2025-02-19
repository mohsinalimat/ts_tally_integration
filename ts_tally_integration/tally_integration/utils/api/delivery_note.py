import frappe
from datetime import datetime
import json
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_delivery():

    delivery_doc = frappe.db.get_all('Delivery Note',filters={'name':'DN-25-00003','is_return':0,'docstatus':1},fields=['*'])

    all_vouchers = []
    final_voucher = []
    for doc in delivery_doc:

        link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': doc['company']}, fields=['parent'])
        address = frappe.db.get_all('Address', filters={'name': link[0]['parent']} if link else {}, fields=['*'])

        cus_link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': doc['customer']}, fields=['parent'])
        cus_address = frappe.db.get_all('Address', filters={'name': cus_link[0]['parent']} if cus_link else {}, fields=['*'])

        customer = frappe.db.get_all('Customer', filters = {'name': doc.customer_name}, fields = ['*'])

        cus_ship_address = []
        # if doc.update_stock == 1:
        cus_ship_link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': doc['customer']}, fields=['parent'])
        cus_ship_address = frappe.db.get_all('Address', filters={'name': cus_ship_link[0]['parent']} if cus_ship_link else {}, fields=['*'])

        company_details = frappe.db.get_all('Company', filters = {'name': doc.company}, fields = ['*'])

        company_idx = (frappe.db.sql(f"select company_number from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['company_number']

        cust_gstin = frappe.get_doc('Customer', doc.customer)

        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(cust_gstin.gst_category, cust_gstin.gst_category)


        sl_entry = frappe.db.get_all('Stock Ledger Entry', filters = {'voucher_no':doc.name}, fields = ['*'])

        for invoice in sl_entry:
            amount = invoice['incoming_rate'] if 'incoming_rate' in invoice and invoice['incoming_rate'] else invoice['outgoing_rate']
            cr_dr = "Cr" if 'credit' in invoice and invoice['credit'] else "Dr"

            delivery_note_item = frappe.db.get_all('Delivery Note Item', filters={'parent':doc.name}, fields=['*'])
            ledgername = doc.customer

            for item in delivery_note_item:
                hsn_desc = frappe.db.get_value('GST HSN Code', {'name': item['gst_hsn_code']}, 'description')

                ledger_dict ={
                        "Autoid": "1",
                        "CompanyNumber": company_idx,
                        "TallyMasterid": 1,
                        "Voucherid": doc.name,
                        "VoucherNumber": doc.name,
                        "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                        "VoucherType": "Delivery Note",
                        "VoucherTypeParent": "Delivery Note",
                        "LedgerName": ledgername,
                        "LedgerParent": "Sundry Debtors",

                        "LedgerAddress": cus_address[0]['city'] if cus_address else "", 
                        "LedgerState": cus_address[0]['state'] if cus_address  else "", 
                        "LedgerCountry": cus_address[0]['country'] if cus_address else "", 
                        "LedgerPincode": cus_address[0]['pincode'] if cus_address else "", 
                        "LedgerMobile": cus_address[0]['phone'] if cus_address else "", 
                        "LedgerGstReg": gst_category if gst_category else "", 
                        "LedgerPan": customer[0]['pan'] if customer[0]['pan'] else "", 
                        "LedgerGstin": cust_gstin.gstin if cust_gstin.gstin else "",

                        "BillName": doc.name,
                        "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                        "CrDr": cr_dr,
                        "CostCategory": "",
                        "CostCentre": item['cost_center'],
                        "Stockitem": "",
                        "Godown": "",
                        "BatchNo": "",
                        "Quantity": "",
                        "Rate": "",
                        "Discount": "",
                        "Amount": amount,
                        "OrderNo": "",
                        "OrderDate": "",
                        "TrackingNo": "",
                        "TrackingDate": "",
                        "TermsOfPayment": "",
                        "OtherRef": "",
                        "TermsOfDelivery1": "",
                        "TermsOfDelivery2": "",
                        "DeliveryNoteNo1":"",
                        "DeliveryNoteDate1":"",
                        "DeliveryNoteNo2":"",
                        "DeliveryNoteDate2":"",		
                        "DeliveryNoteNo3":"",
                        "DeliveryNoteDate3":"",
                        "DeliveryNoteNo4":"",
                        "DeliveryNoteDate4":"",
                        "DeliveryNoteNo5":"",
                        "DeliveryNoteDate5":"",		
                        "DeliveryNoteNo6":"",
                        "DeliveryNoteDate6":"",
                        "DeliveryNoteNo7":"",
                        "DeliveryNoteDate7":"",
                        "DeliveryNoteNo8":"",
                        "DeliveryNoteDate8":"",
                        "DeliveryNoteNo9":"",
                        "DeliveryNoteDate9":"",
                        "DeliveryNoteNo10":"",
                        "DeliveryNoteDate10":"",		
                        "DispatchDocNo": "",
                        "ReceiptDocNo": "",
                        "DispatchedThrough": "",
                        "Destination": "",
                        "CarrierName": "",
                        "BillOfLanding": "",
                        "BillOfLandingDate": "",
                        "VehicleNo": "",

                        "BuyerName": doc.customer if doc.customer else "",
                        "BuyerMailingName": doc.customer if doc.customer else "",
                        "BuyerAddress1": cus_address[0]['address_line1'] if cus_address[0]['address_line1'] else "",
                        "BuyerAddress2": cus_address[0]['address_line2'] if cus_address[0]['address_line2'] else "",
                        "BuyerState": cus_address[0]['state'] if cus_address[0]['state'] else "",
                        "BuyerCountry": cus_address[0]['country'] if cus_address[0]['country'] else "",
                        "BuyerGstReg": gst_category if gst_category else "",
                        "BuyerGSTIN": cust_gstin.gstin if cust_gstin.gstin else "",
                        "BuyerPincode": cus_address[0]['pincode'] if cus_address[0]['pincode'] else "",

                        "ConsigneeName": cus_ship_address[0]['address_title'] if cus_ship_address[0]['address_title'] else "",
                        "ConsigneeMailingName": cus_ship_address[0]['address_title'] if cus_ship_address[0]['address_title'] else "",
                        "ConsigneeAddress1": cus_ship_address[0]['address_title'] if cus_ship_address[0]['address_title'] else "",
                        "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if cus_ship_address[0]['address_line2'] else "",
                        "ConsigneeState": cus_ship_address[0]['state'] if cus_ship_address[0]['state'] else "",
                        "ConsigneeCountry": cus_ship_address[0]['country'] if cus_ship_address[0]['country'] else "",
                        "ConsigneeGSTIN": cust_gstin.gstin if cust_gstin.gstin else "",
                        "ConsigneePincode": cus_ship_address[0]['pincode'] if cus_ship_address[0]['pincode'] else "",
                        "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address[0]['state'] else "",
                        "Reference":"786",
                        "ReferenceDate":"29-10-2022",
                        "Narration": ""
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

