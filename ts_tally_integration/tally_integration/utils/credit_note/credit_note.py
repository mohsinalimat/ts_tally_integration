import frappe
from datetime import datetime

@frappe.whitelist(allow_guest = True)
def credit_note():
    sales_doc = frappe.db.get_all('Sales Invoice',filters={'name':'SINV-24-00017', 'is_return':1},fields=['*'])
    all_vouchers = []
    for doc in sales_doc:
        link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': doc['company']}, fields=['parent'])
        address = frappe.db.get_all('Address', filters={'name': link[0]['parent']} if link else {}, fields=['*'])

        cus_link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': doc['customer']}, fields=['parent'])
        cus_address = frappe.db.get_all('Address', filters={'name': cus_link[0]['parent']} if cus_link else {}, fields=['*'])

        cus_ship_address = []
        if doc.update_stock == 1:
            cus_ship_link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': doc['customer']}, fields=['parent'])
            cus_ship_address = frappe.db.get_all('Address', filters={'name': cus_ship_link[0]['parent']} if cus_ship_link else {}, fields=['*'])

        company_details = frappe.db.get_all('Company', filters = {'name': doc.company}, fields = ['*'])

        company_idx = (frappe.db.sql(f"select idx from `tabTS Tally Company` where company_name ='{doc.company}'", as_dict=True))[0]['idx']

        gstin = frappe.get_doc('Customer', doc.customer)

        gst_category = {
            "Unregistered": "Unregistered/Consumer",
            "Registered Regular": "Regular",
            "Registered Composition": "Composition",
            "SEZ": "Regular - SEZ"
        }.get(gstin.gst_category, gstin.gst_category)


        gl_entry = frappe.db.get_all('GL Entry', filters = {'voucher_no':doc.name}, fields = ['*'])
        vouchers = []


        for invoice in gl_entry:
            amount = invoice['credit'] if 'credit' in invoice and invoice['credit'] else invoice['debit']
            cr_dr = "Cr" if 'credit' in invoice and invoice['credit'] else "Dr"
            
            account_type = frappe.db.get_value('Account', invoice['account'], 'account_type')
            if account_type == 'Income Account':
                ledgername = invoice['account']
                parent_acc = "Sales Accounts"

            elif account_type == 'Bank':
                ledgername = invoice['account']
                parent_acc = "Bank Accounts"

            elif account_type == 'Round Off':
                ledgername = invoice['account']
                parent_acc = "Indirect Expenses"

            elif account_type == 'Stock':
                ledgername = invoice['account']
                parent_acc = "Stock In hand"

            elif account_type == 'Receivable':
                ledgername = doc.customer
                parent_acc = "Sundry Debtors"

            elif account_type == 'Cost of Goods Sold':
                ledgername = invoice['account']
                parent_acc = "Cost of Goods Sold"

            elif account_type == 'Tax':
                ledgername = invoice['account']
                parent_acc = "Duties & Taxes"



            sales_entry = {
                "Autoid": "711",
                "CompanyNumber": str(company_idx),
                "TallyMasterid": 1,
                "Voucherid": doc.name,
                "VoucherNumber": doc.name,
                "VoucherDate": doc.posting_date,
                "VoucherType": 'sales',
                "VoucherTypeParent": "Sales Account",
                "LedgerName": ledgername.split(" - ")[0],
                "LedgerParent": parent_acc,
                "LedgerAddress": address[0]['city'] if address else "",
                "LedgerState": address[0]['state'] if address else "",
                "LedgerCountry": address[0]['country'] if address else "",
                "LedgerPincode": address[0]['pincode'],
                "LedgerMobile": company_details[0]['phone_no'],
                "LedgerGstReg": gst_category,
                "LedgerPan": company_details[0]['pan'],
                "LedgerGstin": gstin.gstin,
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

                "BuyerName": doc.customer,
                "BuyerMailingName": doc.customer,
                "BuyerAddress1": cus_address[0]['address_line1'] if cus_address else "",
                "BuyerAddress2": cus_address[0]['address_line1'] if cus_address else "",
                "BuyerState": cus_address[0]['state'] if cus_address else "",
                "BuyerCountry": cus_address[0]['country'] if cus_address else "",
                "BuyerGstReg": gst_category,
                "BuyerGSTIN": cus_address[0]['gstin'] if cus_address else "",
                "BuyerPincode": cus_address[0]['pincode'] if cus_address else "",

                "ConsigneeName": cus_ship_address[0]['address_title'] if cus_ship_address else "",
                "ConsigneeMailingName":cus_ship_address[0]['address_title'] if cus_ship_address else "",
                "ConsigneeAddress1": cus_ship_address[0]['address_line1'] if cus_ship_address else "",
                "ConsigneeAddress2": cus_ship_address[0]['address_line2'] if cus_ship_address else "",
                "ConsigneeState": cus_ship_address[0]['state'] if cus_ship_address else "",
                "ConsigneeCountry": cus_ship_address[0]['country'] if cus_ship_address else "",
                "ConsigneeGSTIN": cus_ship_address[0]['gstin'] if cus_ship_address else "",
                "ConsigneePincode": cus_ship_address[0]['pincode'] if cus_ship_address else "",

                "PlaceOfSupply": cus_ship_address[0]['state'] if cus_ship_address else "",
                                "CmpGstRegistrationType":"",
                                "CmpGstin":"",
                                "CmpGstState":"",
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

