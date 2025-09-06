import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response
from itertools import chain


@frappe.whitelist(allow_guest=True)
def get_debit_note(company_id=None):
    if company_id == None:
        return Response(json.dumps("Company ID is not found!", default=str), content_type='application/json', status=404)

    tally_company_table = frappe.get_value("TS Tally Company", {"company_number" : company_id}, ["company_name", "stock"], as_dict=1)
    
    if not tally_company_table:
        return Response(json.dumps("Company is not found. Please check the company id!", default=str), content_type='application/json', status=404)

    if tally_company_table.stock == "Inventory":
        empty = ({
            "status": True,
            "VOUCHERDETAILS": {
                "VOUCHER": []
                }
            })
        return Response(json.dumps(empty, default=str), content_type='application/json')

    doc_list = frappe.get_all('Purchase Invoice',
                               filters = {'docstatus': 1, "company" : tally_company_table.company_name, "update_stock":0, 'is_return': 1, 'custom_tally_guid': ['in', ['', None]]},
                               fields = ['*'])

    list_of_purchases= []

    for doc in doc_list:
        supplier = frappe.get_doc("Supplier", doc.supplier)
        supplier_add = frappe.get_doc("Address",supplier.supplier_primary_address)
        list_of_purchases.append(purchase_invoice_json(get_tagged_accounts_amount(doc.name), supplier, supplier_add, doc, company_id))

    response_purchase = {
        "status": True,
        "VOUCHERDETAILS": {
            "VOUCHER": list(chain.from_iterable(list_of_purchases))
        }
    }

    return Response(json.dumps(response_purchase, default=str), content_type='application/json', status=200)

def get_tagged_accounts_amount(purchase_invoice_name):

    account_amount = {}
    gl_entries = frappe.get_all("GL Entry", filters={"voucher_type": "Purchase Invoice", "voucher_no": purchase_invoice_name}, fields=["*"], order_by="creation asc")

    for entry in gl_entries:
        account = entry.account

        normalized_account = account
        if 'Input Tax' in account:
            normalized_account = 'Input Tax' 
        
        if entry.debit is not None and entry.debit > 0:
            if normalized_account in account_amount:
                account_amount[normalized_account]['debit'] += entry.debit
            else:
                account_amount[normalized_account] = {'debit': entry.debit, 'credit': 0}

        elif entry.credit is not None and entry.credit > 0:
            if normalized_account in account_amount:
                account_amount[normalized_account]['credit'] += entry.credit
            else:
                account_amount[normalized_account] = {'debit': 0, 'credit': entry.credit}

    for account, amounts in account_amount.items():
        if amounts['debit'] > 0 and amounts['credit'] > 0:
            amounts['credit'] = abs(amounts['debit'] - amounts['credit'])
            amounts['debit'] = 0


    def custom_sort_key(account):
        if 'creditors' in account.lower():
            return 1
        elif 'write off' in account.lower():
            return 2
        elif 'tax' in account.lower():
            return 3
        elif 'round off' in account.lower():
            return 5
        else:
            return 4

  
    sorted_account_amount = dict(sorted(account_amount.items(), key=lambda item: custom_sort_key(item[0])))
   
    return (sorted_account_amount)

def purchase_invoice_json(tagged_acc, supplier, supplier_add, doc, company_id):

    document = frappe.get_doc("Purchase Invoice", doc.name)
    company = frappe.get_doc("Company", doc.company)
    company_state = frappe.get_value("Address", {"name":document.billing_address}, fieldname="state") if document.billing_address else ""
    cost_center = frappe.get_doc("Cost Center", doc.cost_center) if document.cost_center else ""
    gst_category = {
        "Unregistered": "Unregistered/Consumer",
        "Registered Regular": "Regular",
        "Registered Composition": "Composition",
        "SEZ": "Regular - SEZ"
    }.get(supplier.gst_category, supplier.gst_category)

    gst_category_company = {
        "Unregistered": "Unregistered/Consumer",
        "Registered Regular": "Regular",
        "Registered Composition": "Composition",
        "SEZ": "Regular - SEZ"
    }.get(company.gst_category, company.gst_category)

    list_of_purchase_invoices = []
    
    for key, value in tagged_acc.items():
        if value['debit'] > 0:
            if "Creditors" in key:
                parent_acc = frappe.get_doc("Account", key)
                doc_json = {
                        "Autoid": document.name,
                        "CompanyNumber": str(company_id),
                        "TallyMasterid": 1,
                        "Voucherid": document.name,
                        "VoucherNumber": document.name,
                        "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                        "VoucherType": "Debit Note",
                        "VoucherTypeParent": "Debit Note",
                        "LedgerName": supplier.supplier_name,
                        "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                        "LedgerAddress": supplier_add.address_line1 if supplier_add.address_line1 else "",
                        "LedgerState": supplier_add.state if supplier_add.state else "",
                        "LedgerCountry": supplier_add.country if supplier_add.country else "",
                        "LedgerPincode": supplier_add.pincode if supplier_add.pincode else "",
                        "LedgerMobile": supplier.mobile_no if supplier.mobile_no else "",
                        "LedgerGstReg": gst_category if gst_category else "",
                        "LedgerPan": supplier.pan if supplier.pan else "",
                        "LedgerGstin": supplier.gstin if supplier.gstin else "",
                        "BillName": document.name,
                        "BillDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                        "CrDr":"Dr",
                        "CostCategory": "",
                        "CostCentre": (cost_center.company) if cost_center else "",
                        "Stockitem": "",
                        "Godown": "",
                        "BatchNo": "",
                        "Quantity": "",
                        "Rate": "",
                        "Discount": "",
                        "Amount": str(value['debit']),
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
                        "BuyerName": supplier.supplier_name,
                        "BuyerMailingName": supplier.supplier_name,
                        "BuyerAddress1": supplier_add.address_line1 if supplier_add.address_line1 else "",
                        "BuyerAddress2": supplier_add.address_line2 if supplier_add.address_line2 else "",
                        "BuyerState": supplier_add.state if supplier_add.state else "",
                        "BuyerCountry": supplier_add.country if supplier_add.country else "",
                        "BuyerGstReg": gst_category if gst_category else "",
                        "BuyerGSTIN": supplier.gstin if supplier.gstin else "",
                        "BuyerPincode": supplier_add.pincode if supplier_add.pincode else "",
                        "ConsigneeName": supplier.supplier_name,
                        "ConsigneeMailingName": supplier.supplier_name,
                        "ConsigneeAddress1": supplier_add.address_line1 if supplier_add.address_line1 else "",
                        "ConsigneeAddress2": supplier_add.address_line2 if supplier_add.address_line2 else "",
                        "ConsigneeState": supplier_add.state if supplier_add.state else "",
                        "ConsigneeCountry": supplier_add.country if supplier_add.country else "",
                        "ConsigneeGSTIN": supplier.gstin if supplier.gstin else "",
                        "ConsigneePincode": supplier_add.pincode if supplier_add.pincode else "",
                        "PlaceOfSupply": (document.place_of_supply).split("-")[1] if document.place_of_supply else "",
                        "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                        "CmpGstin": company.gstin if company.gstin else "",
                        "CmpGstState": company_state if company_state else "",
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
                        "Reference": document.bill_no if document.bill_no else "",
                        "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                        "VoucherSourceGodown": "",				
                        "Narration": (document.remarks).replace("\n",". ") if document.remarks else "",
                    }
                list_of_purchase_invoices.append(doc_json)
            
            elif "Cost of Goods Sold" in key:
                pass
            
            else:
                parent_acc = frappe.get_doc("Account", key)
                doc_json = {
                        "Autoid": document.name,
                        "CompanyNumber": str(company_id),
                        "TallyMasterid": 1,
                        "Voucherid": document.name,
                        "VoucherNumber": document.name,
                        "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                        "VoucherType": "Debit Note",
                        "VoucherTypeParent": "Debit Note",
                        "LedgerName": "Roundoff"  if "Rounded Off" in key or "Round Off" in key else (key).split(" - ")[0],
                        "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                        "LedgerAddress":"",
                        "LedgerState": "",
                        "LedgerCountry": "",
                        "LedgerPincode": "",
                        "LedgerMobile": "",
                        "LedgerGstReg": "",
                        "LedgerPan": "",
                        "LedgerGstin": "",
                        "BillName": "",
                        "BillDate": "",
                        "CrDr":"Dr",
                        "CostCategory": "",
                        "CostCentre": (cost_center.company) if cost_center else "",
                        "Stockitem": "",
                        "Godown": "",
                        "BatchNo": "",
                        "Quantity": "",
                        "Rate": "",
                        "Discount": "",
                        "Amount": str(value['debit']),
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
                        "BuyerName": "",
                        "BuyerMailingName": "",
                        "BuyerAddress1": "",
                        "BuyerAddress2": "",
                        "BuyerState": "",
                        "BuyerCountry": "",
                        "BuyerGstReg": "",
                        "BuyerGSTIN": "",
                        "BuyerPincode": "",
                        "ConsigneeName": "",
                        "ConsigneeMailingName": "",
                        "ConsigneeAddress1": "",
                        "ConsigneeAddress2": "",
                        "ConsigneeState": "",
                        "ConsigneeCountry": "",
                        "ConsigneeGSTIN": "",
                        "ConsigneePincode": "",
                        "PlaceOfSupply": "",
                        "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                        "CmpGstin": company.gstin if company.gstin else "",
                        "CmpGstState": company_state if company_state else "",
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
                        "Reference": document.bill_no if document.bill_no else "",
                        "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                        "VoucherSourceGodown": "",				
                        "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                    }
                list_of_purchase_invoices.append(doc_json)

        elif value['credit'] > 0:
            if 'Creditors' in key:
                parent_acc = frappe.get_doc("Account", key)
                doc_json = {
                        "Autoid": document.name,
                        "CompanyNumber": str(company_id),
                        "TallyMasterid": 1,
                        "Voucherid": document.name,
                        "VoucherNumber": document.name,
                        "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                        "VoucherType": "Debit Note",
                        "VoucherTypeParent": "Debit Note",
                        "LedgerName": supplier.supplier_name,
                        "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                        "LedgerAddress": supplier_add.address_line1 if supplier_add.address_line1 else "",
                        "LedgerState": supplier_add.state if supplier_add.state else "",
                        "LedgerCountry": supplier_add.country if supplier_add.country else "",
                        "LedgerPincode": supplier_add.pincode if supplier_add.pincode else "",
                        "LedgerMobile": supplier.mobile_no if supplier.mobile_no else "",
                        "LedgerGstReg": gst_category if gst_category else "",
                        "LedgerPan": supplier.pan if supplier.pan else "",
                        "LedgerGstin": supplier.gstin if supplier.gstin else "",
                        "BillName": document.name,
                        "BillDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                        "CrDr":"Cr",
                        "CostCategory": "",
                        "CostCentre": (cost_center.company) if cost_center else "",
                        "Stockitem": "",
                        "Godown": "",
                        "BatchNo": "",
                        "Quantity": "",
                        "Rate": "",
                        "Discount": "",
                        "Amount": str(value['credit']),
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
                        "BuyerName": supplier.supplier_name,
                        "BuyerMailingName": supplier.supplier_name,
                        "BuyerAddress1": supplier_add.address_line1 if supplier_add.address_line1 else "",
                        "BuyerAddress2": supplier_add.address_line2 if supplier_add.address_line2 else "",
                        "BuyerState": supplier_add.state if supplier_add.state else "",
                        "BuyerCountry": supplier_add.country if supplier_add.country else "",
                        "BuyerGstReg": gst_category if gst_category else "",
                        "BuyerGSTIN": supplier.gstin if supplier.gstin else "",
                        "BuyerPincode": supplier_add.pincode if supplier_add.pincode else "",
                        "ConsigneeName": supplier.supplier_name,
                        "ConsigneeMailingName": supplier.supplier_name,
                        "ConsigneeAddress1": supplier_add.address_line1 if supplier_add.address_line1 else "",
                        "ConsigneeAddress2": supplier_add.address_line2 if supplier_add.address_line2 else "",
                        "ConsigneeState": supplier_add.state if supplier_add.state else "",
                        "ConsigneeCountry": supplier_add.country if supplier_add.country else "",
                        "ConsigneeGSTIN": supplier.gstin if supplier.gstin else "",
                        "ConsigneePincode": supplier_add.pincode if supplier_add.pincode else "",
                        "PlaceOfSupply": (document.place_of_supply).split("-")[1] if document.place_of_supply else "",
                        "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                        "CmpGstin": company.gstin if company.gstin else "",
                        "CmpGstState": company_state if company_state else "",
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
                        "Reference": document.bill_no if document.bill_no else "",
                        "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                        "VoucherSourceGodown": "",				
                        "Narration": (document.remarks).replace("\n",". ") if document.remarks else "",
                    }
                list_of_purchase_invoices.append(doc_json)
            
            elif "Input Tax" in key:
                
                items_tax = frappe.db.sql(f"""
                                SELECT 
                                    parent,
                                    cgst_rate, 
                                    sgst_rate, 
                                    igst_rate, 
                                    SUM(cgst_amount) AS cgst_amount, 
                                    SUM(sgst_amount) AS sgst_amount, 
                                    SUM(igst_amount) AS igst_amount 
                                FROM `tabPurchase Invoice Item` 
                                WHERE parent='{doc.name}' AND docstatus=1
                                GROUP BY parent, cgst_rate, sgst_rate, igst_rate
                            """, as_dict=True)

                for item_tax in items_tax:
                    if item_tax['igst_rate']>0 and item_tax['cgst_rate']==0 and item_tax['sgst_rate']==0:
                        parent_acc = frappe.get_doc("Account", "Input Tax IGST - "+str(company.abbr))
                        doc_json_igst ={
                            "Autoid": document.name,
                            "CompanyNumber": str(company_id),
                            "TallyMasterid": 1,
                            "Voucherid": document.name,
                            "VoucherNumber": document.name,
                            "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "VoucherType": "Debit Note",
                            "VoucherTypeParent": "Debit Note",
                            "LedgerName": "Input Tax IGST @ "+str(item_tax['igst_rate']),
                            "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                            "LedgerAddress":"",
                            "LedgerState": "",
                            "LedgerCountry": "",
                            "LedgerPincode": "",
                            "LedgerMobile": "",
                            "LedgerGstReg": "",
                            "LedgerPan": "",
                            "LedgerGstin": "",
                            "BillName": "",
                            "BillDate": "",
                            "CrDr": "Cr",
                            "CostCategory": "",
                            "CostCentre": (cost_center.company) if cost_center else "",
                            "Stockitem": "",
                            "Godown": "",
                            "BatchNo": "",
                            "Quantity": "",
                            "Rate": "",
                            "Discount": "",
                            "Amount": str(abs(item_tax['igst_amount'])),
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
                            "BuyerName": "",
                            "BuyerMailingName": "",
                            "BuyerAddress1": "",
                            "BuyerAddress2": "",
                            "BuyerState": "",
                            "BuyerCountry": "",
                            "BuyerGstReg": "",
                            "BuyerGSTIN": "",
                            "BuyerPincode": "",
                            "ConsigneeName": "",
                            "ConsigneeMailingName": "",
                            "ConsigneeAddress1": "",
                            "ConsigneeAddress2": "",
                            "ConsigneeState": "",
                            "ConsigneeCountry": "",
                            "ConsigneeGSTIN": "",
                            "ConsigneePincode": "",
                            "PlaceOfSupply": "",
                            "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                            "CmpGstin": company.gstin if company.gstin else "",
                            "CmpGstState": company_state if company_state else "",
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
                            "Reference": document.bill_no if document.bill_no else "",
                            "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                            "VoucherSourceGodown": "",				
                            "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                        }
                        list_of_purchase_invoices.append(doc_json_igst)
                    elif item_tax['igst_rate']==0 and item_tax['cgst_rate']>0 and item_tax['sgst_rate']>0:
                        parent_acc = frappe.get_doc("Account", "Input Tax CGST - "+str(company.abbr))
                        doc_json_cgst ={
                            "Autoid": document.name,
                            "CompanyNumber": str(company_id),
                            "TallyMasterid": 1,
                            "Voucherid": document.name,
                            "VoucherNumber": document.name,
                            "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "VoucherType": "Debit Note",
                            "VoucherTypeParent": "Debit Note",
                            "LedgerName": "Input Tax CGST @ "+str(item_tax['cgst_rate']),
                            "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                            "LedgerAddress":"",
                            "LedgerState": "",
                            "LedgerCountry": "",
                            "LedgerPincode": "",
                            "LedgerMobile": "",
                            "LedgerGstReg": "",
                            "LedgerPan": "",
                            "LedgerGstin": "",
                            "BillName": "",
                            "BillDate": "",
                            "CrDr": "Cr",
                            "CostCategory": "",
                            "CostCentre": (cost_center.company) if cost_center else "",
                            "Stockitem": "",
                            "Godown": "",
                            "BatchNo": "",
                            "Quantity": "",
                            "Rate": "",
                            "Discount": "",
                            "Amount": str(abs(item_tax['cgst_amount'])),
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
                            "BuyerName": "",
                            "BuyerMailingName": "",
                            "BuyerAddress1": "",
                            "BuyerAddress2": "",
                            "BuyerState": "",
                            "BuyerCountry": "",
                            "BuyerGstReg": "",
                            "BuyerGSTIN": "",
                            "BuyerPincode": "",
                            "ConsigneeName": "",
                            "ConsigneeMailingName": "",
                            "ConsigneeAddress1": "",
                            "ConsigneeAddress2": "",
                            "ConsigneeState": "",
                            "ConsigneeCountry": "",
                            "ConsigneeGSTIN": "",
                            "ConsigneePincode": "",
                            "PlaceOfSupply": "",
                            "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                            "CmpGstin": company.gstin if company.gstin else "",
                            "CmpGstState": company_state if company_state else "",
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
                            "Reference": document.bill_no if document.bill_no else "",
                            "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                            "VoucherSourceGodown": "",				
                            "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                        }
                        list_of_purchase_invoices.append(doc_json_cgst)
                        parent_acc = frappe.get_doc("Account", "Input Tax SGST - "+str(company.abbr))
                        doc_json_sgst ={
                            "Autoid": document.name,
                            "CompanyNumber": str(company_id),
                            "TallyMasterid": 1,
                            "Voucherid": document.name,
                            "VoucherNumber": document.name,
                            "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                            "VoucherType": "Debit Note",
                            "VoucherTypeParent": "Debit Note",
                            "LedgerName": "Input Tax SGST @ "+str(item_tax['sgst_rate']),
                            "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                            "LedgerAddress":"",
                            "LedgerState": "",
                            "LedgerCountry": "",
                            "LedgerPincode": "",
                            "LedgerMobile": "",
                            "LedgerGstReg": "",
                            "LedgerPan": "",
                            "LedgerGstin": "",
                            "BillName": "",
                            "BillDate": "",
                            "CrDr": "Cr",
                            "CostCategory": "",
                            "CostCentre": (cost_center.company) if cost_center else "",
                            "Stockitem": "",
                            "Godown": "",
                            "BatchNo": "",
                            "Quantity": "",
                            "Rate": "",
                            "Discount": "",
                            "Amount": str(abs(item_tax['sgst_amount'])),
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
                            "BuyerName": "",
                            "BuyerMailingName": "",
                            "BuyerAddress1": "",
                            "BuyerAddress2": "",
                            "BuyerState": "",
                            "BuyerCountry": "",
                            "BuyerGstReg": "",
                            "BuyerGSTIN": "",
                            "BuyerPincode": "",
                            "ConsigneeName": "",
                            "ConsigneeMailingName": "",
                            "ConsigneeAddress1": "",
                            "ConsigneeAddress2": "",
                            "ConsigneeState": "",
                            "ConsigneeCountry": "",
                            "ConsigneeGSTIN": "",
                            "ConsigneePincode": "",
                            "PlaceOfSupply": "",
                            "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                            "CmpGstin": company.gstin if company.gstin else "",
                            "CmpGstState": company_state if company_state else "",
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
                            "Reference": document.bill_no if document.bill_no else "",
                            "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                            "VoucherSourceGodown": "",				
                            "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                        }
                        list_of_purchase_invoices.append(doc_json_sgst)

            elif "Stock Received But Not Billed" in key or "Cost of Goods Sold" in key:
                parent_acc = frappe.get_doc("Account", key)
                for row in document.items:
                    ledger_name = ''
                    if row.cgst_rate>0 and row.sgst_rate>0 and row.igst_rate==0:
                        ledger_name = f"PURCHASE @ {row.cgst_rate + row.sgst_rate} % {row.gst_hsn_code}"
                    elif row.cgst_rate==0 and row.sgst_rate==0 and row.igst_rate>0:
                        ledger_name = f"PURCHASE @ {row.igst_rate} % {row.gst_hsn_code}"
                    elif row.cgst_rate==0 and row.sgst_rate==0 and row.igst_rate==0:
                        ledger_name = f"PURCHASE Exempt {row.gst_hsn_code}"
                    if key == row.expense_account:
                        if 'Input GST Out-state' in document.taxes_and_charges:
                            doc_json ={
                                "Autoid": document.name,
                                "CompanyNumber": str(company_id),
                                "TallyMasterid": 1,
                                "Voucherid": document.name,
                                "VoucherNumber": document.name,
                                "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                "VoucherType": "Debit Note",
                                "VoucherTypeParent": "Debit Note",
                                "LedgerName": ledger_name if ledger_name!="" else "PURCHASE",
                                "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                                "LedgerAddress":"",
                                "LedgerState": "",
                                "LedgerCountry": "",
                                "LedgerPincode": "",
                                "LedgerMobile": "",
                                "LedgerGstReg": "",
                                "LedgerPan": "",
                                "LedgerGstin": "",
                                "BillName": "",
                                "BillDate": "",
                                "CrDr": "Cr",
                                "CostCategory": "",
                                "CostCentre": (cost_center.company) if cost_center else "",
                                "Stockitem": "",
                                "Godown": "",
                                "BatchNo": "",
                                "Quantity": "",
                                "Rate": "",
                                "Discount": "",
                                "Amount": str(abs(row.net_amount)) if row.net_amount else "",
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
                                "BuyerName": "",
                                "BuyerMailingName": "",
                                "BuyerAddress1": "",
                                "BuyerAddress2": "",
                                "BuyerState": "",
                                "BuyerCountry": "",
                                "BuyerGstReg": "",
                                "BuyerGSTIN": "",
                                "BuyerPincode": "",
                                "ConsigneeName": "",
                                "ConsigneeMailingName": "",
                                "ConsigneeAddress1": "",
                                "ConsigneeAddress2": "",
                                "ConsigneeState": "",
                                "ConsigneeCountry": "",
                                "ConsigneeGSTIN": "",
                                "ConsigneePincode": "",
                                "PlaceOfSupply": "",
                                "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                                "CmpGstin": company.gstin if company.gstin else "",
                                "CmpGstState": company_state if company_state else "",
                                "GstOvrdnTaxability": "Exempt" if row.gst_treatment == "Exempted" or row.gst_treatment == "Non-GST" or row.gst_treatment == "Nil-Rated" else row.gst_treatment or "",
                                "GstOvrdnTypeofsupply":"Goods",
                                "GstHsnName":row.gst_hsn_code if row.gst_hsn_code else "",
                                "GstHsnDescription":frappe.get_value("GST HSN Code",row.gst_hsn_code,"description") if frappe.get_value("GST HSN Code",row.gst_hsn_code,"description") else "",
                                "CgstGstRateDutyhead":"CGST",
                                "CgstGstRateValuationtype":"Based on Value",
                                "CgstGstRate":str(row.igst_rate/2) if row.igst_rate>0 else "",
                                "SgstGstRateDutyhead":"SGST/UTGST",
                                "SgstGstRateValuationtype":"Based on Value",
                                "SgstGstRate":str(row.igst_rate/2) if row.igst_rate>0 else "",
                                "IgstGstRateDutyhead":"IGST",
                                "IgstGstRateValuationtype":"Based on Value",
                                "IgstGstRate":str(row.igst_rate) if row.igst_rate>0 else "",
                                "Reference": document.bill_no if document.bill_no else "",
                                "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                                "VoucherSourceGodown": "",				
                                "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                            }
                            list_of_purchase_invoices.append(doc_json)

                        elif 'Input GST In-state' in document.taxes_and_charges:
                            doc_json ={
                                "Autoid": document.name,
                                "CompanyNumber": str(company_id),
                                "TallyMasterid": 1,
                                "Voucherid": document.name,
                                "VoucherNumber": document.name,
                                "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                "VoucherType": "Debit Note",
                                "VoucherTypeParent": "Debit Note",
                                "LedgerName": ledger_name if ledger_name!="" else "PURCHASE",
                                "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                                "LedgerAddress":"",
                                "LedgerState": "",
                                "LedgerCountry": "",
                                "LedgerPincode": "",
                                "LedgerMobile": "",
                                "LedgerGstReg": "",
                                "LedgerPan": "",
                                "LedgerGstin": "",
                                "BillName": "",
                                "BillDate": "",
                                "CrDr": "Cr",
                                "CostCategory": "",
                                "CostCentre": (cost_center.company) if cost_center else "",
                                "Stockitem": "",
                                "Godown": "",
                                "BatchNo": "",
                                "Quantity": "",
                                "Rate": "",
                                "Discount": "",
                                "Amount": str(abs(row.net_amount)) if row.net_amount else "",
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
                                "BuyerName": "",
                                "BuyerMailingName": "",
                                "BuyerAddress1": "",
                                "BuyerAddress2": "",
                                "BuyerState": "",
                                "BuyerCountry": "",
                                "BuyerGstReg": "",
                                "BuyerGSTIN": "",
                                "BuyerPincode": "",
                                "ConsigneeName": "",
                                "ConsigneeMailingName": "",
                                "ConsigneeAddress1": "",
                                "ConsigneeAddress2": "",
                                "ConsigneeState": "",
                                "ConsigneeCountry": "",
                                "ConsigneeGSTIN": "",
                                "ConsigneePincode": "",
                                "PlaceOfSupply": "",
                                "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                                "CmpGstin": company.gstin if company.gstin else "",
                                "CmpGstState": company_state if company_state else "",
                                "GstOvrdnTaxability": "Exempt" if row.gst_treatment == "Exempted" or row.gst_treatment == "Non-GST" or row.gst_treatment == "Nil-Rated" else row.gst_treatment or "",
                                "GstOvrdnTypeofsupply":"Goods",
                                "GstHsnName":row.gst_hsn_code if row.gst_hsn_code else "",
                                "GstHsnDescription":frappe.get_value("GST HSN Code",row.gst_hsn_code,"description") if frappe.get_value("GST HSN Code",row.gst_hsn_code,"description") else "",
                                "CgstGstRateDutyhead":"CGST",
                                "CgstGstRateValuationtype":"Based on Value",
                                "CgstGstRate":str(row.cgst_rate) if row.cgst_rate>0 else "",
                                "SgstGstRateDutyhead":"SGST/UTGST",
                                "SgstGstRateValuationtype":"Based on Value",
                                "SgstGstRate":str(row.sgst_rate) if row.sgst_rate>0 else "",
                                "IgstGstRateDutyhead":"IGST",
                                "IgstGstRateValuationtype":"Based on Value",
                                "IgstGstRate":str(row.cgst_rate+row.sgst_rate) if row.cgst_rate>0 and row.sgst_rate>0 else "",
                                "Reference": document.bill_no if document.bill_no else "",
                                "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                                "VoucherSourceGodown": "",				
                                "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                            }
                            list_of_purchase_invoices.append(doc_json)

                        else:
                            doc_json ={
                                "Autoid": document.name,
                                "CompanyNumber": str(company_id),
                                "TallyMasterid": 1,
                                "Voucherid": document.name,
                                "VoucherNumber": document.name,
                                "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                                "VoucherType": "Debit Note",
                                "VoucherTypeParent": "Debit Note",
                                "LedgerName": ledger_name if ledger_name!="" else "PURCHASE",
                                "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                                "LedgerAddress":"",
                                "LedgerState": "",
                                "LedgerCountry": "",
                                "LedgerPincode": "",
                                "LedgerMobile": "",
                                "LedgerGstReg": "",
                                "LedgerPan": "",
                                "LedgerGstin": "",
                                "BillName": "",
                                "BillDate": "",
                                "CrDr": "Cr",
                                "CostCategory": "",
                                "CostCentre": (cost_center.company) if cost_center else "",
                                "Stockitem": "",
                                "Godown": "",
                                "BatchNo": "",
                                "Quantity": "",
                                "Rate": "",
                                "Discount": "",
                                "Amount": str(abs(row.net_amount)) if row.net_amount else "",
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
                                "BuyerName": "",
                                "BuyerMailingName": "",
                                "BuyerAddress1": "",
                                "BuyerAddress2": "",
                                "BuyerState": "",
                                "BuyerCountry": "",
                                "BuyerGstReg": "",
                                "BuyerGSTIN": "",
                                "BuyerPincode": "",
                                "ConsigneeName": "",
                                "ConsigneeMailingName": "",
                                "ConsigneeAddress1": "",
                                "ConsigneeAddress2": "",
                                "ConsigneeState": "",
                                "ConsigneeCountry": "",
                                "ConsigneeGSTIN": "",
                                "ConsigneePincode": "",
                                "PlaceOfSupply": "",
                                "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                                "CmpGstin": company.gstin if company.gstin else "",
                                "CmpGstState": company_state if company_state else "",
                                "GstOvrdnTaxability": "Exempt" if row.gst_treatment == "Exempted" or row.gst_treatment == "Non-GST" or row.gst_treatment == "Nil-Rated" else row.gst_treatment or "",
                                "GstOvrdnTypeofsupply":"Goods",
                                "GstHsnName":row.gst_hsn_code if row.gst_hsn_code else "",
                                "GstHsnDescription":frappe.get_value("GST HSN Code",row.gst_hsn_code,"description") if frappe.get_value("GST HSN Code",row.gst_hsn_code,"description") else "",
                                "CgstGstRateDutyhead":"CGST",
                                "CgstGstRateValuationtype":"Based on Value",
                                "CgstGstRate":"",
                                "SgstGstRateDutyhead":"SGST/UTGST",
                                "SgstGstRateValuationtype":"Based on Value",
                                "SgstGstRate":"",
                                "IgstGstRateDutyhead":"IGST",
                                "IgstGstRateValuationtype":"Based on Value",
                                "IgstGstRate":"",
                                "Reference": document.bill_no if document.bill_no else "",
                                "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                                "VoucherSourceGodown": "",				
                                "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                            }
                            list_of_purchase_invoices.append(doc_json)

            else:
                parent_acc = frappe.get_doc("Account", key)
                doc_json ={
                    "Autoid": document.name,
                    "CompanyNumber": str(company_id),
                    "TallyMasterid": 1,
                    "Voucherid": document.name,
                    "VoucherNumber": document.name,
                    "VoucherDate": datetime.strptime(str(document.posting_date),'%Y-%m-%d').strftime('%d-%m-%Y'),
                    "VoucherType": "Debit Note",
                    "VoucherTypeParent": "Debit Note",
                    "LedgerName": "Roundoff"  if "Rounded Off" in key or "Round Off" in key else (key).split(" - ")[0],
                    "LedgerParent": (parent_acc.custom_tally_parent_account) if parent_acc.custom_tally_parent_account else "",
                    "LedgerAddress":"",
                    "LedgerState": "",
                    "LedgerCountry": "",
                    "LedgerPincode": "",
                    "LedgerMobile": "",
                    "LedgerGstReg": "",
                    "LedgerPan": "",
                    "LedgerGstin": "",
                    "BillName": "",
                    "BillDate": "",
                    "CrDr":"Cr",
                    "CostCategory": "",
                    "CostCentre": (cost_center.company) if cost_center else "",
                    "Stockitem": "",
                    "Godown": "",
                    "BatchNo": "",
                    "Quantity": "",
                    "Rate": "",
                    "Discount": "",
                    "Amount": str(value['credit']),
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
                    "BuyerName": "",
                    "BuyerMailingName": "",
                    "BuyerAddress1": "",
                    "BuyerAddress2": "",
                    "BuyerState": "",
                    "BuyerCountry": "",
                    "BuyerGstReg": "",
                    "BuyerGSTIN": "",
                    "BuyerPincode": "",
                    "ConsigneeName": "",
                    "ConsigneeMailingName": "",
                    "ConsigneeAddress1": "",
                    "ConsigneeAddress2": "",
                    "ConsigneeState": "",
                    "ConsigneeCountry": "",
                    "ConsigneeGSTIN": "",
                    "ConsigneePincode": "",
                    "PlaceOfSupply": "",
                    "CmpGstRegistrationType":gst_category_company if gst_category_company else "",
                    "CmpGstin": company.gstin if company.gstin else "",
                    "CmpGstState": company_state if company_state else "",
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
                    "Reference": document.bill_no if document.bill_no else "",
                    "ReferenceDate": datetime.strptime(str(document.bill_date),'%Y-%m-%d').strftime('%d-%m-%Y') if document.bill_date else "",
                    "VoucherSourceGodown": "",				
                    "Narration": (document.remarks).replace("\n",". ") if document.remarks else ""
                }
                list_of_purchase_invoices.append(doc_json)
  
    return list_of_purchase_invoices



@frappe.whitelist(allow_guest=True)
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    purchase_response = data.get("DEBITNOTE RESPONSE", [])

    for item in purchase_response:
        purchase_entry = item.get("AUTOID")
        guid = item.get("GUID")
        ref_no = item.get("REFNO")
        import_date = item.get("IMPORTDATE")
        import_time = item.get("IMPORTTIME")

        # Log incoming item
        frappe.log_error(json.dumps(item, indent=2), "Tally Incoming Purchase Response")

        if not purchase_entry:
            continue

        existing_purchase = frappe.db.get_value("Purchase Invoice", {"name": purchase_entry}, "name")
        if existing_purchase:
            try:
                import_date_obj = datetime.strptime(import_date, "%Y%m%d").date()
                import_time_obj = datetime.strptime(import_time, "%H:%M:%S").time()

                frappe.db.set_value("Purchase Invoice", existing_purchase, {
                    "custom_tally_auto_id": purchase_entry,
                    "custom_tally_guid": guid,
                    "custom_tally_refno": ref_no,
                    "custom_sync_time": datetime.combine(import_date_obj, import_time_obj)
                })

                # Log success update
                frappe.log_error(f"Successfully updated Purchase Invoice: {existing_purchase}", "Tally Sync Success")

            except Exception as dt_err:
                frappe.log_error(f"Date/time parse error for AUTOID {purchase_entry}: {dt_err}", "Tally Date Error")
        else:
            frappe.log_error(f"Purchase Invoice not found for Tally AUTOID: {purchase_entry}", "Tally Purchase Invoice Sync Error")

    response = {
        "status":True,
        "message":"Updated successfully"
    }
    return Response(json.dumps(response, default=str), content_type='application/json')
