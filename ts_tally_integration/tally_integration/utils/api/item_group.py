import frappe
import json
from werkzeug.wrappers import Response
from collections import defaultdict, deque


@frappe.whitelist()
def get_itemgroup(company_id=None):
    if not company_id:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    item_groups = frappe.get_all(
        'Item Group',
        filters={'custom_status': ['!=', 'SUCCESS']},
        fields=['name', 'is_group', 'parent_item_group']
    )

    # Organize item groups by parent
    parent_map = defaultdict(list)
    items_by_name = {}

    for group in item_groups:
        items_by_name[group['name']] = group
        parent = group['parent_item_group'] or 'Primary'
        parent_map[parent].append(group['name'])

    result = []
    visited = set()

    def process_group(group_name):
        if group_name in visited:
            return
        visited.add(group_name)

        group = items_by_name.get(group_name)
        if group:
            item_group_dict = {
                "Autoid": group['name'],
                "CompanyNumber": str(company_id),
                "Name": group['name'],
                "Parent": group['parent_item_group'] or 'Primary',
            }
            result.append(item_group_dict)

        for child in parent_map.get(group_name, []):
            process_group(child)

    # Start from root nodes (parent = 'Primary')
    for root_group in parent_map['Primary']:
        process_group(root_group)

    final_voucher = {
        "status": True,
        "VOUCHERDETAILS": {
            "STOCKGROUPS": result
        }
    }

    response = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    response.status_code = 200
    return response




@frappe.whitelist()
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    item_group_list = data.get("STOCKGROUP RESPONSE", [])

    for item in item_group_list:
        item_group_name = item.get("AUTOID")
        status = item.get("STATUS")
        import_date = item.get("IMPORTDATE")
        import_time = item.get("IMPORTTIME")

        if not item_group_name:
            continue

        existing_item_group = frappe.db.get_value("Item Group", {"name": item_group_name}, "name")
        if existing_item_group:
            try:
                import_date_obj = datetime.strptime(import_date, "%Y%m%d").date()
                import_time_obj = datetime.strptime(import_time, "%H:%M:%S").time()
                sync_datetime = datetime.combine(import_date_obj, import_time_obj)
            except Exception as e:
                frappe.log_error(f"Invalid date/time in response: {item}\nError: {e}", "Tally DateTime Error")
                continue

            frappe.db.set_value('Item Group', existing_item_group, {
                'custom_tally_auto_id': item_group_name,
                'custom_status': status,
                'custom_sync_time': sync_datetime
            })

        else:
            frappe.log_error(f"Item Group not found for Tally AUTOID: {item_group_name}", "Tally Item Sync Error")

    return Response(json.dumps({
        "status":True,
        "message":"Updated successfully"
    }, default=str), content_type='application/json')
