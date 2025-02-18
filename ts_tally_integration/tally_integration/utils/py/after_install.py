from ts_tally_integration.tally_integration.utils.py.user import user_creation
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    print("Creating Tally User...")
    user_creation()
    print("Tally User Created")

    create_account_parentfield()

def create_account_parentfield():
    custom_fields = {
        "Account": [
            {
                "label": "Tally Parent Account",
                "fieldname": "custom_tally_parent_account",
                "fieldtype": "Autocomplete",
                "options":"Sundry Debtors\nDuties & Taxes\nDirect Expenses\nSales Accounts\nPurchase Accounts\nIndirect Expenses\nBank Accounts\nCash-in-Hand",
                "insert_after": "parent_account",
                "depends_on": "eval: doc.is_group == 0",
                "mandatory_depends_on": "eval: doc.is_group == 0",
            }
        ]
    }
    create_custom_fields(custom_fields=custom_fields)
