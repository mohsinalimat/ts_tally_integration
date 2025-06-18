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

    suppliers = frappe.get_list('Supplier', filters = {'custom_status': ['!=', 'SUCCESS']}, fields=['*'])
    
    for supplier in suppliers:

        if supplier.get('supplier_primary_address'):
            supplier_address = frappe.get_list('Address',
                filters={'name': supplier['supplier_primary_address']},
                fields=['*'])
        else:
            supplier_address = []
        

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

    customers = frappe.get_list('Customer', filters = {'custom_status': ['!=', 'SUCCESS']}, fields=['*'])

    for customer in customers:
        if customer.get('customer_primary_address'):
            customer_address = frappe.get_list('Address',
                filters={'name': customer['customer_primary_address']},
                fields=['*'])
        else:
            customer_address = []

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




@frappe.whitelist()
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    parties = data.get("LEDGER RESPONSE", [])

    for party in parties:
        party_name = party.get("AUTOID")
        status = party.get("STATUS")
        import_date = party.get("IMPORTDATE")
        import_time = party.get("IMPORTTIME")

        if not party_name:
            continue

        import_date_obj = datetime.strptime(import_date, "%Y%m%d").date()
        import_time_obj = datetime.strptime(import_time, "%H:%M:%S").time()
        sync_time = datetime.combine(import_date_obj, import_time_obj)

        updated = False

        if frappe.db.exists("Customer", {"name": party_name}):
            frappe.db.set_value('Customer', party_name, {
                'custom_tally_auto_id': party_name,
                'custom_status': status,
                'custom_sync_time': sync_time
            })
            updated = True

        if frappe.db.exists("Supplier", {"name": party_name}):
            frappe.db.set_value('Supplier', party_name, {
                'custom_tally_auto_id': party_name,
                'custom_status': status,
                'custom_sync_time': sync_time
            })
            updated = True

        if not updated:
            frappe.log_error(f"Neither Customer nor Supplier found for Tally AUTOID: {party_name}", "Tally Sync Error")

    return Response(json.dumps({
        "status":True,
        "message":"Updated successfully"
    }, default=str), content_type='application/json')
