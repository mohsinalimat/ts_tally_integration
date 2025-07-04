import frappe
from datetime import datetime
import json
from werkzeug.wrappers import Response


@frappe.whitelist()
def get_delivery_note(company_id = None):
    if company_id == None:
        return Response(json.dumps('Company Number not found!', default=str), content_type='application/json')

    stock = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['stock'])
    if stock == 'Non-Inventory':
        empty = ({
            "status": True,
            "VOUCHERDETAILS": {
                "VOUCHER": []
                }
            })
        return Response(json.dumps(empty, default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    company_address_link = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': company_name}, fields=['parent'])
    company_address = frappe.get_list('Address', filters={'name': company_address_link[0]['parent']} if company_address_link else {}, fields=['*'])
    company_gst = frappe.get_value('Company', {'name': company_name}, ['gstin'])

    all_vouchers = []

    delivery_notes = frappe.get_list('Delivery Note',
                                 filters={'name':'DN-25-00003','company':company_name, 'is_return':0,'docstatus':1},
                                 fields=['*'])

    for doc in delivery_notes:
        if doc.customer_address:
            cus_address = frappe.get_list('Address', filters={'name': doc.customer_address}, fields=['*'])
        else:
            cus_address = []
        customer_pan = frappe.get_value('Customer', {'name': doc.customer_name}, ['pan'])

        cus_ship_link = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': doc['customer']}, fields=['parent'])
        cus_ship_address = frappe.get_list('Address', filters={'name': cus_ship_link[0]['parent']} if cus_ship_link else {}, fields=['*'])

        cust_gstin = frappe.get_doc('Customer', doc.customer)

        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(cust_gstin.gst_category, cust_gstin.gst_category)

        parent_account = 'Sundry Debtors'

        ledger_dict = {
            "Autoid": doc.name,
            "CompanyNumber": str(company_id),
            "TallyMasterid": 1,
            "Voucherid": doc.name,
            "VoucherNumber": doc.name,
            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "VoucherType": 'Delivery Note',
            "VoucherTypeParent": "Delivery Note",
            "LedgerName": f"{doc.customer_name}",
            "LedgerParent": parent_account,

            "LedgerAddress": cus_address[0]['city'] if cus_address and parent_account== "Sundry Debtors" else "", 
            "LedgerState": cus_address[0]['state'] if cus_address and parent_account== "Sundry Debtors" else "", 
            "LedgerCountry": cus_address[0]['country'] if cus_address and parent_account== "Sundry Debtors" else "", 
            "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_account== "Sundry Debtors" else "", 
            "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_account== "Sundry Debtors" else "", 
            "LedgerGstReg": gst_category if parent_account== "Sundry Debtors" else "", 
            "LedgerPan": customer_pan if parent_account== "Sundry Debtors" else "", 
            "LedgerGstin": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",

            "BillName": doc.name,
            "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
            "CrDr": "Dr",
            "CostCategory": "",
            "CostCentre": '',
            "Stockitem": '',
            "Godown": '',
            "BatchNo": '',
            "Quantity": '',
            "Rate": '',
            "Discount": "",
            "Amount": doc.rounded_total,
            "OrderNo": "",
            "OrderDate": "",
            "TrackingNo": "",
            "TrackingDate": "",
            "TermsOfPayment": "",
            "OtherRef": "",
            "TermsOfDelivery1": "",
            "TermsOfDelivery2": "",
            "DispatchDocNo": "",
            "ReceiptDocNo": "",
            "DispatchedThrough": "",
            "Destination": "",
            "CarrierName": "",
            "BillOfLanding": "",
            "BillOfLandingDate": "",
            "VehicleNo": "",

            "BuyerName": doc.customer if parent_account== "Sundry Debtors" else "",
            "BuyerMailingName": doc.customer if parent_account== "Sundry Debtors" else "",
            "BuyerAddress1": cus_address[0]['address_line1'] if parent_account== "Sundry Debtors" and cus_address else "",
            "BuyerAddress2": cus_address[0]['address_line2'] if parent_account== "Sundry Debtors" and cus_address else "",
            "BuyerState": cus_address[0]['state'] if parent_account== "Sundry Debtors" and cus_address else "",
            "BuyerCountry": cus_address[0]['country'] if parent_account== "Sundry Debtors" and cus_address else "",
            "BuyerGstReg": gst_category if parent_account== "Sundry Debtors" else "",
            "BuyerGSTIN": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",
            "BuyerPincode": cus_address[0]['pincode'] if parent_account== "Sundry Debtors" and cus_address else "",

            "ConsigneeName": cus_ship_address[0]['address_title'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
            "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
            "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
            "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
            "ConsigneeState": cus_ship_address[0]['state'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
            "ConsigneeCountry": cus_ship_address[0]['country'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
            "ConsigneeGSTIN": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",
            "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
            "PlaceOfSupply" : doc.place_of_supply,

            "Reference":"",
            "ReferenceDate":"",
            "Narration": ""
        }

        all_vouchers.append(ledger_dict)


        delivery_note_item = frappe.get_all('Delivery Note Item',
                                 filters={'parent':doc.name},
                                 fields=['*'])


        for item_list in delivery_note_item:

            parent_account = 'Duties & Taxes'

            ledger_dict = {
                "Autoid": doc.name,
                "CompanyNumber": str(company_id),
                "TallyMasterid": 1,
                "Voucherid": doc.name,
                "VoucherNumber": doc.name,
                "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "VoucherType": 'Delivery Note',
                "VoucherTypeParent": "Delivery Note",
                "LedgerName": f"Output Tax CGST @ {item_list['cgst_rate']}",
                "LedgerParent": parent_account,

                "LedgerAddress": cus_address[0]['city'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerState": cus_address[0]['state'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerCountry": cus_address[0]['country'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerGstReg": gst_category if parent_account== "Sundry Debtors" else "", 
                "LedgerPan": customer_pan if parent_account== "Sundry Debtors" else "", 
                "LedgerGstin": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",

                "BillName": doc.name,
                "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "CrDr": '',
                "CostCategory": "",
                "CostCentre": '',
                "Stockitem": '',
                "Godown": '',
                "BatchNo": '',
                "Quantity": '',
                "Rate": '',
                "Discount": "",
                "Amount": item_list.amount,
                "OrderNo": "",
                "OrderDate": "",
                "TrackingNo": "",
                "TrackingDate": "",
                "TermsOfPayment": "",
                "OtherRef": "",
                "TermsOfDelivery1": "",
                "TermsOfDelivery2": "",
                "DispatchDocNo": "",
                "ReceiptDocNo": "",
                "DispatchedThrough": "",
                "Destination": "",
                "CarrierName": "",
                "BillOfLanding": "",
                "BillOfLandingDate": "",
                "VehicleNo": "",

                "BuyerName": doc.customer if parent_account== "Sundry Debtors" else "",
                "BuyerMailingName": doc.customer if parent_account== "Sundry Debtors" else "",
                "BuyerAddress1": cus_address[0]['address_line1'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerAddress2": cus_address[0]['address_line2'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerState": cus_address[0]['state'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerCountry": cus_address[0]['country'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerGstReg": gst_category if parent_account== "Sundry Debtors" else "",
                "BuyerGSTIN": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",
                "BuyerPincode": cus_address[0]['pincode'] if parent_account== "Sundry Debtors" and cus_address else "",

                "ConsigneeName": cus_ship_address[0]['address_title'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeState": cus_ship_address[0]['state'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeCountry": cus_ship_address[0]['country'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeGSTIN": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",
                "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "PlaceOfSupply" : doc.place_of_supply,

                "Reference":"",
                "ReferenceDate":"",
                "Narration": ""
            }

            all_vouchers.append(ledger_dict)


        ledger_dict =  {
                "Autoid": doc.name,
                "CompanyNumber": str(company_id),
                "TallyMasterid": 1,
                "Voucherid": doc.name,
                "VoucherNumber": doc.name,
                "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "VoucherType": 'Delivery Note',
                "VoucherTypeParent": "Delivery Note",
                "LedgerName": "Round Off",
                "LedgerParent": "Indirect Expenses",

                "LedgerAddress": cus_address[0]['city'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerState": cus_address[0]['state'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerCountry": cus_address[0]['country'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_account== "Sundry Debtors" else "", 
                "LedgerGstReg": gst_category if parent_account== "Sundry Debtors" else "", 
                "LedgerPan": customer_pan if parent_account== "Sundry Debtors" else "", 
                "LedgerGstin": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",

                "BillName": doc.name,
                "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                "CrDr": '',
                "CostCategory": "",
                "CostCentre": '',
                "Stockitem": '',
                "Godown": '',
                "BatchNo": '',
                "Quantity": '',
                "Rate": '',
                "Discount": "",
                "Amount": doc.rounding_adjustment,
                "OrderNo": "",
                "OrderDate": "",
                "TrackingNo": "",
                "TrackingDate": "",
                "TermsOfPayment": "",
                "OtherRef": "",
                "TermsOfDelivery1": "",
                "TermsOfDelivery2": "",
                "DispatchDocNo": "",
                "ReceiptDocNo": "",
                "DispatchedThrough": "",
                "Destination": "",
                "CarrierName": "",
                "BillOfLanding": "",
                "BillOfLandingDate": "",
                "VehicleNo": "",

                "BuyerName": doc.customer if parent_account== "Sundry Debtors" else "",
                "BuyerMailingName": doc.customer if parent_account== "Sundry Debtors" else "",
                "BuyerAddress1": cus_address[0]['address_line1'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerAddress2": cus_address[0]['address_line2'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerState": cus_address[0]['state'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerCountry": cus_address[0]['country'] if parent_account== "Sundry Debtors" and cus_address else "",
                "BuyerGstReg": gst_category if parent_account== "Sundry Debtors" else "",
                "BuyerGSTIN": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",
                "BuyerPincode": cus_address[0]['pincode'] if parent_account== "Sundry Debtors" and cus_address else "",

                "ConsigneeName": cus_ship_address[0]['address_title'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeState": cus_ship_address[0]['state'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeCountry": cus_ship_address[0]['country'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "ConsigneeGSTIN": cust_gstin.gstin if parent_account== "Sundry Debtors" else "",
                "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_account== "Sundry Debtors" and cus_ship_address else "",
                "PlaceOfSupply" : doc.place_of_supply,

                "Reference":"",
                "ReferenceDate":"",
                "Narration": ""
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
    data = json.loads(response) if isinstance(response, str) else response
    delivery_response = data.get("DELIVERYNOTE RESPONSE", [])

    for response in delivery_response:
        delivery_note_entry = response.get("AUTOID")
        guid = response.get("GUID")
        ref_no = response.get("REFNO")
        import_date = response.get("IMPORTDATE")
        import_time = response.get("IMPORTTIME")

        if not existing_delivery:
            continue

        existing_delivery = frappe.db.get_value("Delivery Note", {"name": delivery_note_entry}, "name")
        if existing_delivery:
            import_date = datetime.strptime(import_date, "%Y%m%d").date()
            import_time = datetime.strptime(import_time, "%H:%M:%S").time()

            frappe.db.set_value("Delivery Note", existing_delivery, {
                "custom_tally_auto_id": existing_delivery,
                "custom_tally_guid": guid,
                "custom_tally_refno": ref_no,
                "custom_sync_time": datetime.combine(import_date, import_time)
            })

        else:
            frappe.log_error(f"Delivery Note not found for Tally AUTOID: {existing_delivery}", "Tally Delivery Note Sync Error")

    response =  {
        "status":True,
        "message":"Updated successfully"
        }
    return Response(json.dumps(response, default=str), content_type='application/json')

