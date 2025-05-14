import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist()
def get_party(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')
    auto_id = 1
    all_doc = []

    suppliers = frappe.get_list('Supplier', fields=['*'])
    
    for supplier in suppliers:

        supplier_address = frappe.get_list('Address',
                                           filters={'name': supplier['supplier_primary_address']},
                                           fields=['*'])

        supplier_dict = {
                "Autoid": auto_id,
                "CompanyNumber": str(company_id),
                "LedgerName": supplier.name,
                "LedgerParent": "Sundry Creditors",
                "LedgerAddress": supplier_address[0]['city'] if supplier_address else '',
                "LedgerState": supplier_address[0]['state'] if supplier_address else '',
                "LedgerCountry": supplier_address[0]['country'] if supplier_address else '',
                "LedgerPincode": supplier_address[0]['pincode'] if supplier_address else '',
                "LedgerMobile": supplier.mobile_no,
                "LedgerGstReg": "Regular" if supplier_address and supplier_address[0]['gst_category'] == 'Registered Regular' else "Unregistered/Consumer",
                "LedgerPan": supplier.pan if supplier_address and supplier_address[0]['gstin'] else '',
                "LedgerGstin": supplier_address[0]['gstin'] if supplier_address and supplier_address[0]['gstin'] else '',
            }
        auto_id += 1

        all_doc.append(supplier_dict)


    customers = frappe.get_list('Customer', fields=['*'])

    for customer in customers:
        customer_address = frappe.get_list('Address',
                                   filters={'name': customer['customer_primary_address']},
                                   fields=['*'])

        customer_dict = {
            "Autoid": auto_id,
            "CompanyNumber": str(company_id),
            "LedgerName": customer.name,
            "LedgerParent": "Sundry Debtors",
            "LedgerAddress": customer_address[0]['city'] if customer_address else '',
            "LedgerState": customer_address[0]['state'] if customer_address else '',
            "LedgerCountry": customer_address[0]['country'] if customer_address else '',
            "LedgerPincode": customer_address[0]['pincode'] if customer_address else '',
            "LedgerMobile": customer.mobile_no,
            "LedgerGstReg": "Regular" if customer_address and customer_address[0]['gst_category'] == 'Registered Regular' else "Unregistered/Consumer",
            "LedgerPan": customer.pan if customer_address and customer_address[0]['gstin'] else '',
            "LedgerGstin": customer_address[0]['gstin'] if customer_address and customer_address[0]['gstin'] else '',
        }
        auto_id += 1

        all_doc.append(customer_dict)

    final_voucher = ({
        "status": True,
        "VOUCHERDETAILS": {
            "LEDGER": all_doc
        }
    })

    final_voucher = final_voucher
    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200

    return final_voucher
