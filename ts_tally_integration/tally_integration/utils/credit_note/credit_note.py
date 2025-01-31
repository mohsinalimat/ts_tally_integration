import frappe
from datetime import datetime


@frappe.whitelist(allow_guest = True)
def credit_note():
    sales_doc = frappe.db.get_all('Sales Invoice',filters={'name':'SINV-25-00016','is_return':1},fields=['*'])
    all_vouchers = []
    for doc in sales_doc:
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

        company_idx = (frappe.db.sql(f"select idx from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['idx']

        cust_gstin = frappe.get_doc('Customer', doc.customer)

        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(cust_gstin.gst_category, cust_gstin.gst_category)


        gl_entry = frappe.db.get_all('GL Entry', filters = {'voucher_no':doc.name}, fields = ['*'])
        gl_entry = gl_entry[::-1]
        vouchers = []


        for invoice in gl_entry:
            amount = invoice['credit'] if 'credit' in invoice and invoice['credit'] else invoice['debit']
            cr_dr = "Cr" if 'credit' in invoice and invoice['credit'] else "Dr"

            account_type = frappe.db.get_value('Account', invoice['account'], 'account_type')

            if account_type == 'Income Account':
                ledgername = invoice['account']
                parent_acc = "Sales Accounts"

                sales_item = frappe.db.get_all('Sales Invoice Item', filters={'parent':doc.name}, fields=['*'])

                for item in sales_item:
                        hsn_desc = frappe.db.get_value('GST HSN Code', {'name': item['gst_hsn_code']}, 'description')

                        sales_entry = {
                            "Autoid": "711",
                            "CompanyNumber": str(company_idx),
                            "TallyMasterid": 1,
                            "Voucherid": doc.name,
                            "VoucherNumber": doc.name,
                            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "VoucherType": 'Credit Note',
                            "VoucherTypeParent": "Credit Note",
                            "LedgerName": ledgername.split(" - ")[0],
                            "LedgerParent": parent_acc,

                            "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                            "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                            "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                            "BillName": "711",
                            "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "CrDr": cr_dr,
                            "CostCategory": "",
                            "CostCentre": doc.company,
                            "Stockitem": "",
                            "Godown": "",
                            "BatchNo": "",
                            "Quantity": "",
                            "Rate": "",
                            "Discount": "",
                            "Amount": abs(item['amount']),
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

                            "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                            "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                            "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                            "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                            "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                            "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                            "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                            "CmpGstRegistrationType":gst_category,
                                            "CmpGstin":company_details[0]['gstin'],
                                            "CmpGstState":address[0]['state'],
                                            "GstOvrdnTaxability": "Taxable" if item.get('cgst_rate') else "Exempt",
                                            "GstOvrdnTypeofsupply":"Goods",
                                            "GstHsnName":item['gst_hsn_code'],
                                            "GstHsnDescription":hsn_desc,
                                            "CgstGstRateDutyhead":"CGST",
                                            "CgstGstRateValuationtype":"Based on Value",
                                            "CgstGstRate":item['cgst_rate'],
                                            "SgstGstRateDutyhead":"SGST/UTGST",
                                            "SgstGstRateValuationtype":"Based on Value",
                                            "SgstGstRate":item['sgst_rate'],
                                            "IgstGstRateDutyhead":"IGST",
                                            "IgstGstRateValuationtype":"Based on Value",
                                            "IgstGstRate":item['sgst_rate'] + item['cgst_rate'],
                            "Narration": ""
                        }

                        vouchers.append(sales_entry)
                sales_item_processed = True  

                if sales_item_processed:
                    continue

                                # --------------------------------- The BELOW block of code is only for TAX ---------------------------------------------

            elif account_type == 'Tax':
                ledgername = invoice['account']
                parent_acc = "Duties & Taxes"

                sales_item = frappe.db.get_all('Sales Invoice Item', filters={'parent':doc.name}, fields=['*'])

                for item in sales_item:

                    if item['cgst_rate']:
                        sales_entry = {
                            "Autoid": "711",
                            "CompanyNumber": str(company_idx),
                            "TallyMasterid": 1,
                            "Voucherid": doc.name,
                            "VoucherNumber": doc.name,
                            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "VoucherType": 'Credit Note',
                            "VoucherTypeParent": "Credit Note",
                            "LedgerName": f"{ledgername.split(' - ')[0]} @ {item['cgst_rate']}",
                            "LedgerParent": parent_acc,

                            "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                            "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                            "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                            "BillName": "711",
                            "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "CrDr": cr_dr,
                            "CostCategory": "",
                            "CostCentre": doc.company,
                            "Stockitem": "",
                            "Godown": "",
                            "BatchNo": "",
                            "Quantity": "",
                            "Rate": "",
                            "Discount": "",
                            "Amount": abs(item['cgst_amount']),
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

                            "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                            "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                            "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                            "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                            "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                            "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                            "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                            "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                            "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                            "CmpGstRegistrationType":gst_category,
                                            "CmpGstin":company_details[0]['gstin'],
                                            "CmpGstState":address[0]['state'],
                                            "GstOvrdnTaxability":"",
                                            "GstOvrdnTypeofsupply":"",
                                            "GstHsnName":"",
                                            "GstHsnDescription":"",
                                            "CgstGstRateDutyhead":"",
                                            "CgstGstRateValuationtype":"",
                                            "CgstGstRate":"",
                                            "SgstGstRateDutyhead":"",
                                            "SgstGstRateValuationtype":"",
                                            "SgstGstRate":"",
                                            "IgstGstRateDutyhead":"",
                                            "IgstGstRateValuationtype":"",
                                            "IgstGstRate":"",
                            "Narration": ""
                        }

                    if item['sgst_rate']:
                        sales_entry = {
                                "Autoid": "711",
                                "CompanyNumber": str(company_idx),
                                "TallyMasterid": 1,
                                "Voucherid": doc.name,
                                "VoucherNumber": doc.name,
                                "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                "VoucherType": 'Credit Note',
                                "VoucherTypeParent": "Credit Note",
                                "LedgerName": f"{ledgername.split(' - ')[0]} @ {item['sgst_rate']}",
                                "LedgerParent": parent_acc,

                                "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                                "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                                "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                                "BillName": "711",
                                "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                "CrDr": cr_dr,
                                "CostCategory": "",
                                "CostCentre": doc.company,
                                "Stockitem": "",
                                "Godown": "",
                                "BatchNo": "",
                                "Quantity": "",
                                "Rate": "",
                                "Discount": "",
                                "Amount": abs(item['sgst_amount']),
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

                                "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                                "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                                "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                                "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                                "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                                "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                                "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                                "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                                "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                                "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                                "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                                "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                                "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                                "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                                "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                                "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                                "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                                "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                                "CmpGstRegistrationType":gst_category,
                                                "CmpGstin":company_details[0]['gstin'],
                                                "CmpGstState":address[0]['state'],
                                                "GstOvrdnTaxability":"",
                                                "GstOvrdnTypeofsupply":"",
                                                "GstHsnName":"",
                                                "GstHsnDescription":"",
                                                "CgstGstRateDutyhead":"",
                                                "CgstGstRateValuationtype":"",
                                                "CgstGstRate":"",
                                                "SgstGstRateDutyhead":"",
                                                "SgstGstRateValuationtype":"",
                                                "SgstGstRate":"",
                                                "IgstGstRateDutyhead":"",
                                                "IgstGstRateValuationtype":"",
                                                "IgstGstRate":"",
                                "Narration": ""
                            }

                        vouchers.append(sales_entry)

                # --------------------------------- The ABOVE block of code is only for TAX ---------------------------------------------


            elif account_type == 'Bank':
                ledgername = invoice['account']
                parent_acc = "Bank Accounts"

                sales_entry = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'Credit Note',
                    "VoucherTypeParent": "Credit Note",
                    "LedgerName": ledgername.split(" - ")[0],
                    "LedgerParent": parent_acc,

                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                    "BillName": "711",
                    "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "CrDr": cr_dr,
                    "CostCategory": "",
                    "CostCentre": doc.company,
                    "Stockitem": "",
                    "Godown": "",
                    "BatchNo": "",
                    "Quantity": "",
                    "Rate": "",
                    "Discount": "",
                    "Amount": abs(amount),
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

                    "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                    "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                    "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                    "CmpGstRegistrationType":gst_category,
                                    "CmpGstin":company_details[0]['gstin'],
                                    "CmpGstState":address[0]['state'],
                                    "GstOvrdnTaxability":"",
                                    "GstOvrdnTypeofsupply":"",
                                    "GstHsnName":"",
                                    "GstHsnDescription":"",
                                    "CgstGstRateDutyhead":"",
                                    "CgstGstRateValuationtype":"",
                                    "CgstGstRate":"",
                                    "SgstGstRateDutyhead":"",
                                    "SgstGstRateValuationtype":"",
                                    "SgstGstRate":"",
                                    "IgstGstRateDutyhead":"",
                                    "IgstGstRateValuationtype":"",
                                    "IgstGstRate":"",
                    "Narration": ""
                }

                vouchers.append(sales_entry)

            elif account_type == 'Stock':
                ledgername = invoice['account']
                parent_acc = "Stock In hand"

                sales_entry = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'Credit Note',
                    "VoucherTypeParent": "Credit Note",
                    "LedgerName": ledgername.split(" - ")[0],
                    "LedgerParent": parent_acc,

                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                    "BillName": "711",
                    "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "CrDr": cr_dr,
                    "CostCategory": "",
                    "CostCentre": doc.company,
                    "Stockitem": "",
                    "Godown": "",
                    "BatchNo": "",
                    "Quantity": "",
                    "Rate": "",
                    "Discount": "",
                    "Amount": abs(amount),
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

                    "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                    "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                    "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                    "CmpGstRegistrationType":gst_category,
                                    "CmpGstin":company_details[0]['gstin'],
                                    "CmpGstState":address[0]['state'],
                                    "GstOvrdnTaxability":"",
                                    "GstOvrdnTypeofsupply":"",
                                    "GstHsnName":"",
                                    "GstHsnDescription":"",
                                    "CgstGstRateDutyhead":"",
                                    "CgstGstRateValuationtype":"",
                                    "CgstGstRate":"",
                                    "SgstGstRateDutyhead":"",
                                    "SgstGstRateValuationtype":"",
                                    "SgstGstRate":"",
                                    "IgstGstRateDutyhead":"",
                                    "IgstGstRateValuationtype":"",
                                    "IgstGstRate":"",
                    "Narration": ""
                }

                vouchers.append(sales_entry)

            elif account_type == 'Receivable':
                ledgername = doc.customer
                parent_acc = "Sundry Debtors"

                sales_entry = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'Credit Note',
                    "VoucherTypeParent": "Credit Note",
                    "LedgerName": ledgername.split(" - ")[0],
                    "LedgerParent": parent_acc,

                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                    "BillName": "711",
                    "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "CrDr": cr_dr,
                    "CostCategory": "",
                    "CostCentre": doc.company,
                    "Stockitem": "",
                    "Godown": "",
                    "BatchNo": "",
                    "Quantity": "",
                    "Rate": "",
                    "Discount": "",
                    "Amount": abs(amount),
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

                    "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                    "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                    "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                    "CmpGstRegistrationType":gst_category,
                                    "CmpGstin":company_details[0]['gstin'],
                                    "CmpGstState":address[0]['state'],
                                    "GstOvrdnTaxability":"",
                                    "GstOvrdnTypeofsupply":"",
                                    "GstHsnName":"",
                                    "GstHsnDescription":"",
                                    "CgstGstRateDutyhead":"",
                                    "CgstGstRateValuationtype":"",
                                    "CgstGstRate":"",
                                    "SgstGstRateDutyhead":"",
                                    "SgstGstRateValuationtype":"",
                                    "SgstGstRate":"",
                                    "IgstGstRateDutyhead":"",
                                    "IgstGstRateValuationtype":"",
                                    "IgstGstRate":"",
                    "Narration": ""
                }

                vouchers.append(sales_entry)

            elif account_type == 'Cost of Goods Sold':
                ledgername = invoice['account']
                parent_acc = "Cost of Goods Sold"

                sales_entry = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'Credit Note',
                    "VoucherTypeParent": "Credit Note",
                    "LedgerName": ledgername.split(" - ")[0],
                    "LedgerParent": parent_acc,

                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                    "BillName": "711",
                    "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "CrDr": cr_dr,
                    "CostCategory": "",
                    "CostCentre": doc.company,
                    "Stockitem": "",
                    "Godown": "",
                    "BatchNo": "",
                    "Quantity": "",
                    "Rate": "",
                    "Discount": "",
                    "Amount": abs(amount),
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

                    "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                    "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                    "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                    "CmpGstRegistrationType":gst_category,
                                    "CmpGstin":company_details[0]['gstin'],
                                    "CmpGstState":address[0]['state'],
                                    "GstOvrdnTaxability":"",
                                    "GstOvrdnTypeofsupply":"",
                                    "GstHsnName":"",
                                    "GstHsnDescription":"",
                                    "CgstGstRateDutyhead":"",
                                    "CgstGstRateValuationtype":"",
                                    "CgstGstRate":"",
                                    "SgstGstRateDutyhead":"",
                                    "SgstGstRateValuationtype":"",
                                    "SgstGstRate":"",
                                    "IgstGstRateDutyhead":"",
                                    "IgstGstRateValuationtype":"",
                                    "IgstGstRate":"",
                    "Narration": ""
                }

                vouchers.append(sales_entry)

            elif account_type == 'Round Off':
                ledgername = 'Roundoff'
                parent_acc = "Indirect Expenses"

                sales_entry = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'Credit Note',
                    "VoucherTypeParent": "Credit Note",
                    "LedgerName": ledgername.split(" - ")[0],
                    "LedgerParent": parent_acc,

                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                    "BillName": "711",
                    "BillDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "CrDr": cr_dr,
                    "CostCategory": "",
                    "CostCentre": doc.company,
                    "Stockitem": "",
                    "Godown": "",
                    "BatchNo": "",
                    "Quantity": "",
                    "Rate": "",
                    "Discount": "",
                    "Amount": abs(amount),
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

                    "BuyerName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerMailingName": doc.customer if parent_acc == "Sundry Debtors" else "",
                    "BuyerAddress1": cus_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerAddress2": cus_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerState": cus_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerCountry": cus_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_address else "",
                    "BuyerGstReg": gst_category if parent_acc == "Sundry Debtors" else "",
                    "BuyerGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "BuyerPincode": cus_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_address else "",

                    "ConsigneeName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeMailingName": cus_ship_address[0]['address_title'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeState": cus_ship_address[0]['state'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeCountry": cus_ship_address[0]['country'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "ConsigneeGSTIN": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",
                    "ConsigneePincode": cus_ship_address[0]['pincode'] if parent_acc == "Sundry Debtors" and cus_ship_address else "",
                    "PlaceOfSupply" : cus_ship_address[0]['state'] if cus_ship_address and parent_acc == "Sundry Debtors" else "",

                                    "CmpGstRegistrationType":gst_category,
                                    "CmpGstin":company_details[0]['gstin'],
                                    "CmpGstState":address[0]['state'],
                                    "GstOvrdnTaxability":"",
                                    "GstOvrdnTypeofsupply":"",
                                    "GstHsnName":"",
                                    "GstHsnDescription":"",
                                    "CgstGstRateDutyhead":"",
                                    "CgstGstRateValuationtype":"",
                                    "CgstGstRate":"",
                                    "SgstGstRateDutyhead":"",
                                    "SgstGstRateValuationtype":"",
                                    "SgstGstRate":"",
                                    "IgstGstRateDutyhead":"",
                                    "IgstGstRateValuationtype":"",
                                    "IgstGstRate":"",
                    "Narration": ""
                }

                vouchers.append(sales_entry)

        all_vouchers.append({
            "status": True,
            "VOUCHERDETAILS": {
                "VOUCHER": vouchers
            }
        })

    return all_vouchers
