import frappe

def create_bulk_items(count=50):
    for i in range(1, count + 1):
        item_code = f"AUTO-ITEM-{i:03d}"

        if not frappe.db.exists("Item", item_code):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": item_code,
                "item_name": f"Auto Item {i}",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "gst_hsn_code": '999799',
                "is_stock_item": 1,
                "maintain_stock": 1,
                "is_sales_item": 1,
                "is_purchase_item": 1
            })
            item.insert(ignore_permissions=True)

    frappe.db.commit()




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
