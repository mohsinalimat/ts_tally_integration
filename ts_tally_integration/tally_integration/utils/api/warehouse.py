import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_warehouse(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    group_warehouse = []
    nongroup = []

    warehouses = frappe.get_all('Warehouse', filters={'company': company_name}, fields=['*'])
    for warehouse in warehouses:
        if warehouse.is_group:
            warehouse_dict = {
                    "Autoid": "1",
                    "CompanyNumber": str(company_id),
                    "Name": warehouse.warehouse_name,
                    "Parent": frappe.get_value('Warehouse', {'name': warehouse.parent_warehouse}, 'warehouse_name') if warehouse.parent_warehouse else "Primary",
                    "ADDRESS1": "",
                    "ADDRESS2": "",
                    "ADDRESS3": "",
                    "ADDRESS4": ""
                }

            group_warehouse.append(warehouse_dict)

        if not warehouse.is_group:
            warehouse_dict = {
                    "Autoid": "1",
                    "CompanyNumber": str(company_id),
                    "Name": warehouse.warehouse_name,
                    "Parent": frappe.get_value('Warehouse', {'name': warehouse.parent_warehouse}, 'warehouse_name') if warehouse.parent_warehouse else "Primary",
                    "ADDRESS1": "",
                    "ADDRESS2": "",
                    "ADDRESS3": "",
                    "ADDRESS4": ""
                }

            nongroup.append(warehouse_dict)

    final_voucher = ({
        "status": True,
        "VOUCHERDETAILS": {
            "GODOWNS": group_warehouse + nongroup
        }
    })

    final_voucher = final_voucher
    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200

    return final_voucher
