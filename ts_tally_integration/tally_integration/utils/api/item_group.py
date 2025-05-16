import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response
from frappe.utils import now


@frappe.whitelist()
def get_itemgroup(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')
    auto_id = 1
    non_group = []
    group_item_group = []

    item_groups = frappe.get_all('Item Group', fields=['name', 'is_group', 'parent_item_group'])
    for group in item_groups:

        if group.is_group:
            item_group_dict = {
                "Autoid": auto_id,
                "CompanyNumber": str(company_id),
                "Name": group.name,
                "Parent": 'Primary',
            }
            auto_id += 1

            group_item_group.append(item_group_dict)


        if not group.is_group:
            item_group_dict = {
                "Autoid": auto_id,
                "CompanyNumber": str(company_id),
                "Name": group.name,
                "Parent": group.parent_item_group,
            }
            auto_id += 1

            non_group.append(item_group_dict)

    final_voucher = ({
        "status": True,
        "VOUCHERDETAILS": {
            "STOCKGROUPS": group_item_group + non_group
        }
    })

    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200

    return final_voucher



@frappe.whitelist()
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    item_group = data.get("STOCKGROUP RESPONSE", [])

    for item in item_group:
        item_name = item.get("AUTOID")
        status = item.get("STATUS")

        if not item_name:
            continue

        existing_item = frappe.db.get_value("Item Group", {"item_name": item_name}, "name")
        if existing_item:
            doc = frappe.get_doc("Item Group", existing_item)
            doc.custom_tally_auto_id = item_name
            doc.custom_status = status
            doc.custom_sync_time = now()
            doc.save(ignore_permissions=True)
            frappe.db.commit()
        else:
            frappe.log_error(f"Item Group not found for Tally AUTOID: {item_name}", "Tally Item Group Sync Error")
