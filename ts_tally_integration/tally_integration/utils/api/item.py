import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response
from frappe.utils import now

@frappe.whitelist()
def get_item(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    all_doc = []

    items = frappe.get_list('Item', filters={'disabled': 0}, fields=['*'])
    auto_id = 1
    for item in items:
        tax_template = frappe.get_all('Item Tax', filters={'parent': item.name}, fields=['*'])

        # Default taxability
        taxability = ""
        item_tax_template = []

        for i in tax_template:
            item_tax_template = frappe.get_list('Item Tax Template', filters={'company': company_name, 'name': i.item_tax_template}, fields=['*'])
            if item_tax_template:
                taxability = 'Taxable' if item_tax_template[0]['gst_treatment'] == 'Taxable' else ""
            else:
                taxability = ""

        hsn_desc = frappe.get_value('GST HSN Code', {'name': item.gst_hsn_code}, 'description') or ''

        item_dict = {
            "Autoid": auto_id,
            "CompanyNumber": str(company_id),
            "Name": item.item_name,
            "Parent": item.item_group,
            "Category": item.item_group,
            "BaseUnits": item.stock_uom,
            "IsBatchWiseOn": 'Yes' if item.has_batch_no else "No",
            "IsGSTApplicable": "Applicable" if taxability == 'Taxable' else 'Not Applicable',
            "HsnCode": item.gst_hsn_code if taxability == 'Taxable' else '',
            "Hsn": hsn_desc.replace('\n', ' ') if taxability == 'Taxable' else '',
            "Taxability": taxability,
            "CgstRate": str(int(item_tax_template[0]['gst_rate'] / 2)) if item_tax_template else '0',
            "SgstRate": str(int(item_tax_template[0]['gst_rate'] / 2)) if item_tax_template else '0',
            "IgstRate": str(int(item_tax_template[0]['gst_rate'])) if item_tax_template else '0',
            "GSTTypeofSupply": "Goods" if taxability == 'Taxable' else '',
            "GodownName": "",
            "BatchName": "",
            "OpeningBalance": "",
            "OpeningRate": "",
            "OpeningValue": ""
        }
        auto_id += 1

        all_doc.append(item_dict)

    final_voucher = ({
        "status": True,
        "VOUCHERDETAILS": {
            "STOCKITEMS": all_doc
        }
    })


    final_voucher = final_voucher
    final_voucher = Response(json.dumps(final_voucher, default=str), content_type='application/json')
    final_voucher.status_code = 200

    return final_voucher


@frappe.whitelist()
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    items = data.get("STOCKITEM RESPONSE", [])

    for item in items:
        item_name = item.get("AUTOID")
        status = item.get("STATUS")
        import_date = item.get("IMPORTDATE")
        import_time = item.get("IMPORTTIME")

        if not item_name:
            continue

        existing_item = frappe.db.get_value("Item", {"item_name": item_name}, "name")
        if existing_item:
            import_date = datetime.strptime(import_date, "%Y%m%d").date()
            import_time = datetime.strptime(import_time, "%H:%M:%S").time()

            frappe.db.set_value('Item Group', existing_item, {
                'custom_tally_auto_id': item_name,
                'custom_status': status,
                'custom_sync_time': datetime.combine(import_date, import_time)
            })

        else:
            frappe.log_error(f"Item not found for Tally AUTOID: {item_name}", "Tally Item Sync Error")
 
    response =  {
        "status": True,
        "message": "Updated successfully"
        }
    return Response(json.dumps(response, default=str), content_type='application/json')

