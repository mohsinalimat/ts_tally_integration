import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response

@frappe.whitelist()
def get_warehouse(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    group_warehouse = []
    nongroup = []

    warehouses = frappe.get_all('Warehouse',
                                filters={'company': company_name, 'custom_status': ['!=', 'SUCCESS']},
                                fields=['*'])

    for warehouse in warehouses:
        if warehouse.is_group:
            warehouse_dict = {
                    "Autoid": warehouse.warehouse_name,
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
                    "Autoid": warehouse.warehouse_name,
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


@frappe.whitelist()
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    warehouse_response = data.get("GODOWN RESPONSE", [])

    for warehouse in warehouse_response:
        warehouse_name = warehouse.get("AUTOID")
        status = warehouse.get("STATUS")
        import_date = warehouse.get("IMPORTDATE")
        import_time = warehouse.get("IMPORTTIME")
    
        if not warehouse_name:
            continue
        
        existing_warehouse = frappe.db.get_value("Warehouse", {"warehouse_name": warehouse_name}, "name")
        if existing_warehouse:
            import_date = datetime.strptime(import_date, "%Y%m%d").date()
            import_time = datetime.strptime(import_time, "%H:%M:%S").time()

            frappe.db.set_value('Warehouse', existing_warehouse, {
                'custom_tally_auto_id': warehouse_name,
                'custom_status': status,
                'custom_sync_time': datetime.combine(import_date, import_time)
            })

        else:
            frappe.log_error(f"Warehouse not found for Tally AUTOID: {warehouse_name}", "Tally Warehouse Sync Error")
    frappe.db.commit()
    response =  {
        "status":True,
        "message":"Updated successfully"
        }
    return Response(json.dumps(response, default=str), content_type='application/json')
