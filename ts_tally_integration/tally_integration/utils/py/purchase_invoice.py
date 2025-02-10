import frappe

def validate(doc, event):
    list_of_bill = set(frappe.get_all("Purchase Invoice", filters={"bill_no":["is","set"]}, fields=["bill_no"] , pluck="bill_no"))
    if doc.bill_no in list_of_bill:
        frappe.throw(msg="Supplier Invoice No has to be unique !")
