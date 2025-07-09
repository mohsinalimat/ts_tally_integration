import frappe
from datetime import datetime
import json
from werkzeug.wrappers import Response


@frappe.whitelist()
def get_stock_entry(company_id=None):
    import json
    from frappe.utils.response import Response
    from datetime import datetime

    if not company_id:
        return Response(json.dumps('Company Number not found!', default=str), content_type='application/json')

    stock = frappe.get_value('TS Tally Company', {'company_number': company_id}, 'stock')
    if stock == 'Inventory':
        return Response(json.dumps({
            "status": True,
            "VOUCHERDETAILS": {
                "VOUCHER": []
            }
        }, default=str), content_type='application/json')

    company_name = frappe.get_value('TS Tally Company', {'company_number': company_id}, 'company_name')
    all_vouchers = []

    stock_entries = frappe.get_all('Stock Entry', filters={'company': company_name, 'docstatus': 1}, fields=['name', 'posting_date'])

    for entry in stock_entries:
        stock_entry = frappe.get_doc('Stock Entry', entry.name)
        for item in stock_entry.items:
            base_data = {
                "Autoid": str(item.item_name),
                "CompanyNumber": str(company_id),
                "TallyMasterid": 1,
                "Voucherid": stock_entry.name,
                "VoucherNumber": stock_entry.name,
                "VoucherDate": datetime.strptime(str(stock_entry.posting_date), '%Y-%m-%d').strftime('%Y%m%d'),
                "VoucherType": "StockJournal",
                "VoucherTypeParent": "StockJournal",
                "LedgerName": "",
                "LedgerParent": "",
                "LedgerAddress": "",
                "LedgerState": "",
                "LedgerCountry": "",
                "LedgerPincode": "",
                "LedgerMobile": "",
                "LedgerGstReg": "",
                "LedgerGstin": "",
                "BillName": "",
                "BillDate": "",
                "CostCategory": "",
                "CostCentre": "",
                "Stockitem": item.item_name,
                "BatchNo": "",
                "Quantity": float(item.qty),
                "Rate": float(item.basic_rate),
                "Discount": "",
                "Amount": float(item.amount),
                "BuyerName": "",
                "BuyerMailingName": "",
                "BuyerAddress1": "",
                "BuyerAddress2": "",
                "BuyerState": "",
                "BuyerCountry": "",
                "ConsigneeName": "",
                "ConsigneeMailingName": "",
                "ConsigneeAddress1": "",
                "ConsigneeAddress2": "",
                "ConsigneeState": "",
                "ConsigneeCountry": "",
                "Narration": stock_entry.remarks or ""
            }

            # Case 1: Stock Transfer (both warehouses present)
            if item.s_warehouse and item.t_warehouse:
                cr_entry = base_data.copy()
                cr_entry.update({
                    "CrDr": "Cr",
                    "Godown": item.s_warehouse.split('-')[0].strip(),
                    "Void": "out"
                })
                all_vouchers.append(cr_entry)

                dr_entry = base_data.copy()
                dr_entry.update({
                    "CrDr": "Dr",
                    "Godown": item.t_warehouse.split('-')[0].strip(),
                    "Void": "in"
                })
                all_vouchers.append(dr_entry)

            # Case 2: Only Source Warehouse (Consumption)
            elif item.s_warehouse:
                cr_entry = base_data.copy()
                cr_entry.update({
                    "CrDr": "Cr",
                    "Godown": item.s_warehouse.split('-')[0].strip(),
                    "Void": "out"
                })
                all_vouchers.append(cr_entry)

            # Case 3: Only Target Warehouse (Production)
            elif item.t_warehouse:
                dr_entry = base_data.copy()
                dr_entry.update({
                    "CrDr": "Dr",
                    "Godown": item.t_warehouse.split('-')[0].strip(),
                    "Void": "in"
                })
                all_vouchers.append(dr_entry)

            response_data = {
                "status": True,
                "VOUCHERDETAILS": {
                    "VOUCHER": all_vouchers
                }
            }

    response = Response(json.dumps(response_data, default=str), content_type='application/json')
    response.status_code = 200
    return response





@frappe.whitelist()
def fetch_response(response):
    data = json.loads(response) if isinstance(response, str) else response
    stockjournal_response = data.get("STOCKJOURNAL RESPONSE", [])

    for response in stockjournal_response:
        stock_entry_id = response.get("AUTOID")
        guid = response.get("GUID")
        ref_no = response.get("REFNO")
        import_date = response.get("IMPORTDATE")
        import_time = response.get("IMPORTTIME")

        existing_stock_entry = frappe.db.get_value("Stock Entry", {"name": stock_entry_id}, "name")
        if not existing_stock_entry:
            frappe.log_error(f"Stock Entry not found for Tally AUTOID: {stock_entry_id}", "Tally Stock Entry Sync Error")
            continue

        import_date = datetime.strptime(import_date, "%Y%m%d").date()
        import_time = datetime.strptime(import_time, "%H:%M:%S").time()

        frappe.db.set_value("Stock Entry", existing_stock_entry, {
            "custom_tally_auto_id": stock_entry_id,
            "custom_tally_guid": guid,
            "custom_tally_refno": ref_no,
            "custom_sync_time": datetime.combine(import_date, import_time)
        })

        frappe.logger("Tally Sync").info(f"Stock Entry {existing_stock_entry} updated with GUID: {guid}, REFNO: {ref_no}")

    response = {
        "status": True,
        "message": "Updated successfully"
    }
    return Response(json.dumps(response, default=str), content_type='application/json')


