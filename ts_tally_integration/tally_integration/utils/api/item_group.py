import frappe
import json
from werkzeug.wrappers import Response
from datetime import datetime

@frappe.whitelist()
def get_itemgroup(company_id=None):
    if company_id is None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    # Step 1: Fetch all item groups
    item_groups = frappe.get_all(
        'Item Group',
        filters={'custom_tally_auto_id': ["=", ""]},
        fields=['name', 'is_group', 'parent_item_group']
    )

    # Step 2: Build lookup tree
    tree = {}
    group_lookup = {}

    for group in item_groups:
        group_lookup[group['name']] = group
        parent = group['parent_item_group'] or "All Item Groups"

        if parent not in tree:
            tree[parent] = []
        tree[parent].append(group['name'])

    # Step 3: Recursive traversal
    non_group = []
    group_item_group = []

    def traverse(parent):
        children = tree.get(parent, [])
        for child in children:
            group = group_lookup[child]
            item_group_dict = {
                "Autoid": group['name'],
                "CompanyNumber": str(company_id),
                "Name": group['name'],
                "Parent": group['parent_item_group'] or "All Item Groups"
            }

            if group['is_group']:
                group_item_group.append(item_group_dict)
            else:
                non_group.append(item_group_dict)

            traverse(child)

    # Start from actual root
    traverse("All Item Groups")

    # Step 4: Final response
    final_voucher = {
        "status": True,
        "VOUCHERDETAILS": {
            "STOCKGROUPS": group_item_group + non_group
        }
    }

    response = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    response.status_code = 200
    return response




@frappe.whitelist()
def fetch_response(response):
    frappe.log_error(f"Response from Tally: {response}", "Tally Item Group Response")
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
