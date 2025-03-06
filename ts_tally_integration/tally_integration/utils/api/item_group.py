import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_itemgroup(company_id = None):
    # if company_id == None:
    #     return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    # company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    all_doc = []

    item_groups = frappe.get_all('Item Group', fields=['name', 'is_group', 'parent_item_group'])
    for group in item_groups:

        item_group_dict = {
            "Autoid": "1",
            "CompanyNumber": " ",
            "Name": group.name,
            "Parent": group.parent_item_group,
        }

        all_doc.append(item_group_dict)

    final_voucher = ({
        "status": True,
        "VOUCHERDETAILS": {
            "STOCKGROUPS": all_doc
        }
    })

    final_voucher = final_voucher
    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200

    return final_voucher
