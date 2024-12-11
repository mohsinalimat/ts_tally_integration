import frappe
import json
from datetime import datetime

@frappe.whitelist()
def get_sales():
    sales_doc = frappe.db.get_all('Sales Invoice',filters={'status':'paid'},fields=['name', 'customer', 'posting_date', 'company'])
    output = {}
    for doc in sales_doc:
        link = frappe.db.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': doc['company']}, fields=['parent'])
        address = frappe.db.get_all('Address', filters={'name': link[0]['parent']} if link else {}, fields=['state', 'city'])
        company_details = frappe.db.get_list('Company', filters = {'name': doc.company}, fields = ['idx'])
        gstin = frappe.db.get_all('Customer', filters = {'name':doc.customer}, fields = ['gstin','gst_category', 'primary_address'])

        sales_invoice_item = frappe.db.get_all('Sales Invoice Item', filters = {'parent':doc.name}, fields = ['*'])

        sales_entries = []

        for invoice in sales_invoice_item:
            sales_entry = {
                "Autoid": "711",
                "CompanyNumber": company_details[0]['idx'],
                "TallyMasterid": 1,
                "Voucherid": "",
                "VoucherNumber": doc.name,
                "VoucherDate": doc.posting_date,
                "VoucherType": "GST Sales",
                "VoucherTypeParent": "Sales Accounts",
                "LedgerName": doc.customer,
                "LedgerParent": "Sundry Debtors",
                "LedgerAddress": address[0]['city'] if address else "",
                "LedgerState": address[0]['state'] if address else "",
                "LedgerCountry": "India",
                "LedgerPincode": "638452",
                "LedgerMobile": "+919976288522",
                "LedgerGstReg": "Regular",
                "LedgerPan": "",
                "LedgerGstin": gstin[0]['gstin'] if address else "",
                "BillName": "711",
                "BillDate": "01-04-2024",
                "CrDr": "Dr",
                "CostCategory": "",
                "CostCentre": invoice['cost_center'],
                "Stockitem": "",
                "Godown": "",
                "BatchNo": "",
                "Quantity": "",
                "Rate": "",
                "Discount": "",
                "Amount": "12000.00",
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
                "BuyerName": "K.YASOTHA-9976288522",
                "BuyerMailingName": "K.YASOTHA-9976288522",
                "BuyerAddress1": "VELAVAN NAGAR VADUGA PALAYAM GOBI",
                "BuyerAddress2": "",
                "BuyerState": address[0]['state'] if address else "",
                "BuyerCountry": "India",
				"BuyerGstReg":"Regular",
                "BuyerGSTIN": "33AAACH7409R1Z8",
                "BuyerPincode": "638452",
                "ConsigneeName": "K.YASOTHA-9976288522",
                "ConsigneeMailingName": "K.YASOTHA-9976288522",
                "ConsigneeAddress1": "VELAVAN NAGAR VADUGA PALAYAM GOBI",
                "ConsigneeAddress2": "",
                "ConsigneeState": "Tamil Nadu",
                "ConsigneeCountry": "India",
                "ConsigneeGSTIN": "33AAACH7409R1Z8",
                "ConsigneePincode": "638452",
                "PlaceOfSupply": "Tamil Nadu",
                                "CmpGstRegistrationType":"Regular",
                                "CmpGstin":"33AALCP6122E1ZO",
                                "CmpGstState":"Tamil Nadu",
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

            sales_entries.append(sales_entry)
        output[doc['name']] = sales_entries
    return output