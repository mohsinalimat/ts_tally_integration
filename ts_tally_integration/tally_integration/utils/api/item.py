import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist()
def get_item(company_id = None):
    if company_id == None:
        return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    all_doc = []

    items = frappe.get_all('Item', filters={'disabled': 0, 'custom_tally_auto_id': ['!=', '']}, fields=['*'])

    for item in items:
        tax_template = frappe.get_all('Item Tax', filters={'parent': item.name}, fields=['*'])

        # Default taxability
        taxability = ""
        item_tax_template = []

        for i in tax_template:
            item_tax_template = frappe.get_all('Item Tax Template', filters={'company': company_name, 'name': i.item_tax_template}, fields=['*'])
            if item_tax_template:
                taxability = 'Taxable' if item_tax_template[0]['gst_treatment'] == 'Taxable' else ""
            else:
                taxability = ""

        hsn_desc = frappe.get_value('GST HSN Code', {'name': item.gst_hsn_code}, 'description') or ''

        is_gst_applicable = "Applicable" if taxability == 'Taxable' else 'Not Applicable'
        hsn_code = item.gst_hsn_code if is_gst_applicable == 'Applicable' else ''
        hsn_desc_clean = hsn_desc.replace('\n', ' ') if is_gst_applicable == 'Applicable' else ''
        gst_type_of_supply = "Goods" if is_gst_applicable == 'Applicable' else ''
        cgst = "{:.1f}".format(item_tax_template[0]['gst_rate'] / 2) if item_tax_template and is_gst_applicable == 'Applicable' else ""
        sgst = "{:.1f}".format(item_tax_template[0]['gst_rate'] / 2) if item_tax_template and is_gst_applicable == 'Applicable' else ""
        igst = "{:.1f}".format(item_tax_template[0]['gst_rate']) if item_tax_template and is_gst_applicable == 'Applicable' else ""

        item_dict = {
            "Autoid": item.item_name,
            "CompanyNumber": str(company_id),
            "Name": item.item_name,
            "Parent": "All Item Groups",
            "Category": "",
            "BaseUnits": item.stock_uom,
            "IsBatchWiseOn": 'Yes' if item.has_batch_no else "No",
            "IsGSTApplicable": is_gst_applicable,
            "HsnCode": hsn_code,
            "Hsn": hsn_desc_clean,
            "Taxability": taxability if is_gst_applicable == 'Applicable' else '',
            "CgstRate": cgst,
            "SgstRate": sgst,
            "IgstRate": igst,
            "GSTTypeofSupply": gst_type_of_supply,
            "GodownName": "",
            "BatchName": "",
            "OpeningBalance": "",
            "OpeningRate": "",
            "OpeningValue": ""
        }


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
def fetch_response(response=None):
    data = json.loads(response) if isinstance(response, str) else response
    items = data.get("STOCKITEM RESPONSE", [])

    for item in items:
        item_name = item.get("AUTOID")
        status = item.get("STATUS")
        import_date = item.get("IMPORTDATE")
        import_time = item.get("IMPORTTIME")

        if not item_name:
            continue

        item_docname = frappe.db.get_value("Item", {"item_name": item_name}, "name")
        if item_docname:
            item_doc = frappe.get_doc("Item", item_docname)

            item_doc.custom_tally_auto_id = item_name
            item_doc.custom_status = status
            item_doc.custom_sync_time = datetime.combine(
                datetime.strptime(import_date, "%Y%m%d").date(),
                datetime.strptime(import_time, "%H:%M:%S").time()
            )

            item_doc.save(ignore_permissions=True)

            # Log even on successful save
            frappe.log_error(
                title="Tally Item Sync - Success",
                message=f"Item updated successfully: {item_name}"
            )

        else:
            frappe.log_error(
                title="Tally Item Sync Error",
                message=f"Item not found for Tally AUTOID: {item_name}"
            )

    response = {
        "status":True,
        "message":"Updated successfully"
    }
    return Response(json.dumps(response, default=str), content_type='application/json')



