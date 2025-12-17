import frappe

def script():
    receipt_response = [{"AUTOID":"All Warehouses","STATUS":"SUCCESS","IMPORTDATE":"20251217","IMPORTTIME":"17:23:30"},
                        {"AUTOID":"Stores","STATUS":"SUCCESS","IMPORTDATE":"20251217","IMPORTTIME":"17:23:30"}]
    import requests
    import json

    url = "http://106.51.153.24:41635/api/method/ts_tally_integration.tally_integration.utils.api.warehouse.fetch_response"

    headers = {
        "Authorization": "token c538d9013360afc:0868d0f44207d41",
        "Content-Type": "application/json"
    }

    payload = {
        "response": json.dumps({
            "GODOWN RESPONSE": receipt_response
        })
    }

    res = requests.post(url, headers=headers, json=payload)

    print(res.status_code)
    print(res.json())





import frappe

def duplicate_payment_entry(source_pe = 'ACC-PAY-2025-02280', copies=500):
    for i in range(copies):
        new_pe = frappe.copy_doc(
            frappe.get_doc("Payment Entry", source_pe)
        )

        # Reset fields
        new_pe.name = None
        new_pe.docstatus = 0
        new_pe.posting_date = frappe.utils.today()

        new_pe.insert(ignore_permissions=True)

    frappe.db.commit()
