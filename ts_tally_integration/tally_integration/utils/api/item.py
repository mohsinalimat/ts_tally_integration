import frappe
import json
from datetime import datetime
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest = True)
def get_item(company_id = None):
    # if company_id == None:
    #     return Response(json.dumps("Company number not found!", default=str), content_type='application/json')

    # company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, ['company_name'])

    all_doc = []

    items = frappe.get_all('Item', fields=['*'])

    for item in items:
        tax_template = frappe.get_all('Item Tax', filters={'parent': item.name}, fields=['*'])

        item_dict = {
            "Autoid": "22",
            "CompanyNumber": "1",
            "GUID": "77de6783-98f9-479b-961d-0bc4774e95a-0000208a",
            "Name": item.item_name,
            "Parent": item.item_group,
            "Category": item.item_group,
            "BaseUnits": item.stock_uom,
            "IsBatchWiseOn": item.has_batch_no if item.has_batch_no == 1 else " ",
            "IsGSTApplicable": "Applicable",
            "HsnCode": item.gst_hsn_code,
            "Hsn": "INSULIN SYRUP",
            "Taxability": "Taxable",
            "CgstRate": "2.5",
            "SgstRate": "2.5",
            "IgstRate": "5",
            "GSTTypeofSupply": "Goods",
            "GodownName": " ",
            "BatchName": " ",
            "OpeningBalance": " ",
            "OpeningRate": " ",
            "OpeningValue": " "
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
