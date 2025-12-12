import frappe
import json
from werkzeug.wrappers import Response
from datetime import datetime


@frappe.whitelist()
def get_itemgroup(company_id=None):
    if not company_id:
        return Response(json.dumps({"status": False, "message": "Company number not found!"}),
                        content_type="application/json")

    # Fetch item groups ONLY with valid fields
    item_groups = frappe.get_all(
        "Item Group",
        fields=["name", "parent_item_group", "is_group"]
    )

    # Build parent → children map
    tree = {}
    for ig in item_groups:
        parent = ig.parent_item_group or "Primary"
        tree.setdefault(parent, []).append(ig)

    final_list = []

    # Recursive function
    def add_group(parent_name, display_parent):
        children = tree.get(parent_name, [])
        for child in children:

            # Add the group
            final_list.append({
                "Autoid": "1",
                "CompanyNumber": company_id,
                "Name": child.name,
                "Parent": display_parent,
                # "IsGroup": "Yes" if child.is_group else "No"
            })

            # If group has children → recurse
            if child.is_group:
                add_group(child.name, child.name)

    # Start recursion from Primary root
    add_group("Primary", "Primary")

    return Response(json.dumps({
        "status": True,
        "VOUCHERDETAILS": {"STOCKGROUPS": final_list}
    }, default=str), content_type="application/json")





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
