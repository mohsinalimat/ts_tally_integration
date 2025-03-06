import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_warehouse(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    all_doc = []

    warehouses = frappe.get_all('Warehouse', filters={'company': company_name}, fields=['*'])
    for warehouse in warehouses:

        warehouse_dict = {
                "Autoid": "1",
                "CompanyNumber": str(company_id),
                "Name": warehouse.warehouse_name,
                "Parent": frappe.get_value('Warehouse', {'name': warehouse.parent_warehouse}, ['warehouse_name']),
                "ADDRESS1": "",
                "ADDRESS2": "",
                "ADDRESS3": "",
                "ADDRESS4": ""
            }

        all_doc.append(warehouse_dict)

    final_voucher = ({
        "status": True,
        "VOUCHERDETAILS": {
            "GODOWNS": all_doc
        }
    })

    final_voucher = final_voucher
    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200

    return final_voucher
