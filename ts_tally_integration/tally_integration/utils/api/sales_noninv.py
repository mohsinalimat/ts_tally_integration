import frappe
from datetime import datetime
import json
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_sales():

    sales_doc = frappe.db.get_all('Sales Invoice',filters={'name':'SINV-25-00030','is_return':0, 'update_stock':0, 'docstatus':1},fields=['*'])

    all_vouchers = []
    final_voucher = []
    for doc in sales_doc:
        tax_processed = False
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


        gl_entry = frappe.db.get_all('GL Entry', filters = {'voucher_no':doc.name}, fields = ['*'])
        gl_entry = gl_entry[::-1]

        all_vouchers = []

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
                        if item['sgst_rate']:
                            ledger_suffix = item['sgst_rate'] + item['cgst_rate']
                        elif item['gst_treatment'] == 'Exempted':
                            ledger_suffix = 'Exempt'
                        elif item['igst_rate']:
                            ledger_suffix = item['igst_rate']

                        ledger_dict = {
                            "Autoid": "711",
                            "CompanyNumber": str(company_idx),
                            "TallyMasterid": 1,
                            "Voucherid": doc.name,
                            "VoucherNumber": doc.name,
                            "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "VoucherType": 'sales',
                            "VoucherTypeParent": "Sales",
                            "LedgerName": f"{ledgername.split(' - ')[0]} @ {(ledger_suffix)}",
                            "LedgerParent": parent_acc,

                            "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                            "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                            "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                            "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                            "BillName": doc.name,
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
                            "Amount": amount,
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
                                            "GstHsnDescription":hsn_desc.replace('\n', ' '),
                                            "CgstGstRateDutyhead":"CGST",
                                            "CgstGstRateValuationtype":"Based on Value",
                                            "CgstGstRate":item['cgst_rate'] if item['cgst_rate'] else "",
                                            "SgstGstRateDutyhead":"SGST/UTGST",
                                            "SgstGstRateValuationtype":"Based on Value",
                                            "SgstGstRate":item['sgst_rate'] if item['sgst_rate'] else "",
                                            "IgstGstRateDutyhead":"IGST",
                                            "IgstGstRateValuationtype":"Based on Value",
                                            "IgstGstRate": item['sgst_rate'] + item['cgst_rate'] if item['sgst_rate'] and item['cgst_rate'] else "",
                            "Narration": ""
                        }

                        all_vouchers.append(ledger_dict)
                sales_item_processed = True  

                if sales_item_processed:
                    continue

            # --------------------------------- The BELOW block of code is only for TAX ---------------------------------------------


            elif account_type == 'Tax':
                
                if not tax_processed:
                    ledgername = invoice['account']
                    parent_acc = "Duties & Taxes"
                    tax_processed = True

                    items_tax = frappe.db.sql(f"""
                                SELECT 
                                    parent,
                                    item_name,
                                    cgst_rate, 
                                    sgst_rate, 
                                    igst_rate,
                                    gst_treatment,
                                    SUM(cgst_amount) AS cgst_amount, 
                                    SUM(sgst_amount) AS sgst_amount, 
                                    SUM(igst_amount) AS igst_amount 
                                FROM `tabSales Invoice Item` 
                                WHERE parent='{doc.name}'
                                GROUP BY parent, cgst_rate, sgst_rate, igst_rate
                            """, as_dict=True)

                    for item in items_tax:
                        if not item['gst_treatment'] == 'Exempted':
                            if item['cgst_rate']:
                                ledger_dict = {
                                    "Autoid": "711",
                                    "CompanyNumber": str(company_idx),
                                    "TallyMasterid": 1,
                                    "Voucherid": doc.name,
                                    "VoucherNumber": doc.name,
                                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                    "VoucherType": 'sales',
                                    "VoucherTypeParent": "Sales",
                                    "LedgerName": f"Output Tax CGST @ {item['cgst_rate']}",
                                    "LedgerParent": parent_acc,

                                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                                    "BillName": doc.name,
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
                                    "Amount": item['cgst_amount'],
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

                                all_vouchers.append(ledger_dict)


                            if item['sgst_rate']:
                                ledger_dict = {
                                    "Autoid": "711",
                                    "CompanyNumber": str(company_idx),
                                    "TallyMasterid": 1,
                                    "Voucherid": doc.name,
                                    "VoucherNumber": doc.name,
                                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                    "VoucherType": 'sales',
                                    "VoucherTypeParent": "Sales",
                                    "LedgerName": f"Output Tax SGST @ {item['cgst_rate']}",
                                    "LedgerParent": parent_acc,

                                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                                    "BillName": doc.name,
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
                                    "Amount": item['cgst_amount'],
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

                                all_vouchers.append(ledger_dict)

                            if item['igst_rate']:
                                ledger_dict = {
                                    "Autoid": "711",
                                    "CompanyNumber": str(company_idx),
                                    "TallyMasterid": 1,
                                    "Voucherid": doc.name,
                                    "VoucherNumber": doc.name,
                                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                    "VoucherType": 'sales',
                                    "VoucherTypeParent": "Sales",
                                    "LedgerName": f"{ledgername.split(' - ')[0]} @ {item['igst_rate']}",
                                    "LedgerParent": parent_acc,

                                    "LedgerAddress": cus_address[0]['city'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerState": cus_address[0]['state'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerCountry": cus_address[0]['country'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerPincode": cus_address[0]['pincode'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerMobile": cus_address[0]['phone'] if cus_address and parent_acc == "Sundry Debtors" else "", 
                                    "LedgerGstReg": gst_category if parent_acc == "Sundry Debtors" else "", 
                                    "LedgerPan": customer[0]['pan'] if parent_acc == "Sundry Debtors" else "", 
                                    "LedgerGstin": cust_gstin.gstin if parent_acc == "Sundry Debtors" else "",

                                    "BillName": doc.name,
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
                                    "Amount": item['igst_amount'],
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

                                all_vouchers.append(ledger_dict)
                # --------------------------------- The ABOVE block of code is only for TAX ---------------------------------------------


            elif account_type == 'Bank':
                ledgername = invoice['account']
                parent_acc = "Bank Accounts"

                ledger_dict = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'sales',
                    "VoucherTypeParent": "Sales",
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

                    "BillName": doc.name,
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
                    "Amount": amount,
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

                all_vouchers.append(ledger_dict)

            elif account_type == 'Stock':
                ledgername = invoice['account']
                parent_acc = "Stock In hand"

                ledger_dict = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'sales',
                    "VoucherTypeParent": "Sales",
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

                    "BillName": doc.name,
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
                    "Amount": amount,
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

                all_vouchers.append(ledger_dict)

            elif account_type == 'Receivable':
                ledgername = doc.customer
                parent_acc = "Sundry Debtors"

                ledger_dict = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'sales',
                    "VoucherTypeParent": "Sales",
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

                    "BillName": doc.name,
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
                    "Amount": amount,
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

                all_vouchers.append(ledger_dict)

            elif account_type == 'Cost of Goods Sold':
                ledgername = invoice['account']
                parent_acc = "Cost of Goods Sold"

                ledger_dict = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'sales',
                    "VoucherTypeParent": "Sales",
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

                    "BillName": doc.name,
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
                    "Amount": amount,
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

                all_vouchers.append(ledger_dict)

            elif account_type == 'Round Off':
                ledgername = 'Roundoff'
                parent_acc = "Indirect Expenses"

                ledger_dict = {
                    "Autoid": "711",
                    "CompanyNumber": str(company_idx),
                    "TallyMasterid": 1,
                    "Voucherid": doc.name,
                    "VoucherNumber": doc.name,
                    "VoucherDate": datetime.strptime(str(doc.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": 'sales',
                    "VoucherTypeParent": "Sales",
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

                    "BillName": doc.name,
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
                    "Amount": amount,
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
