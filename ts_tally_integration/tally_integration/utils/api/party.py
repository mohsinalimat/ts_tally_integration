import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_party(company_id = None):

    all_doc = []

    suppliers = frappe.get_list('Supplier', fields=['*'])

    for supplier in suppliers:

        supplier_address = frappe.get_list('Address',
                                           filters={'name': supplier['supplier_primary_address']},
                                           fields=['city', 'pincode', 'state', 'country'])

        party_dict = {
                "Autoid": "711",
                "CompanyNumber": "1",
                "LedgerName": supplier.name,
                "LedgerParent": "Sundry Creditors",
                "LedgerAddress": supplier_address[0]['city'] if supplier_address else '',
                "LedgerState": supplier_address[0]['state'] if supplier_address else '',
                "LedgerCountry": supplier_address[0]['country'] if supplier_address else '',
                "LedgerPincode": supplier_address[0]['pincode'] if supplier_address else '',
                "LedgerMobile": supplier.mobile_no,
                "LedgerGstReg": "Regular",
                "LedgerPan": supplier.pan,
                "LedgerGstin": supplier.gstin
            }

        all_doc.append(party_dict)

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
