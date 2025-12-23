import frappe
# from ts_tally_integration.tally_integration.utils.py.user import user_creation
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from ts_tally_integration.tally_integration.doctype.ts_tally_settings.ts_tally_settings import user_creation, role_creation, role_permission


def after_migrate():
    print("Dependencies Installing by Thirvusoft...")
    user_id = "tally@thirvusoft.co.in"
    role_name = "Tally User"
    role_creation(role_name)
    role_permission(role_name)
    user_creation(user_id)
    create_gst_tally_accounts()

    print('Creating Tally Fields')
    create_account_parentfield()
    print("Fields Updated...")

    print("Updating Account's Parent Field by Thirvusoft...")
    create_tally_parent_account()
    print("Account ParentField Updated by Thirvusoft...")



from datetime import datetime

def create_gst_tally_accounts():
    ledgers = [
        # Sales & Purchase
        ("Sales @ 5.0", "Sales Accounts"),
        ("Purchase @ 5.0", "Purchase Accounts"),

        ("Sales @ 12.0", "Sales Accounts"),
        ("Purchase @ 12.0", "Purchase Accounts"),

        ("Sales @ 18.0", "Sales Accounts"),
        ("Purchase @ 18.0", "Purchase Accounts"),

        ("Sales @ 28.0", "Sales Accounts"),
        ("Purchase @ 28.0", "Purchase Accounts"),

        ("Sales @ Exempt", "Sales Accounts"),
        ("Purchase @ Exempt", "Purchase Accounts"),

        # Input Tax
        ("Input Tax CGST @ 2.5", "Duties & Taxes"),
        ("Input Tax SGST @ 2.5", "Duties & Taxes"),
        ("Input Tax IGST @ 5.0", "Duties & Taxes"),

        ("Input Tax CGST @ 6.0", "Duties & Taxes"),
        ("Input Tax SGST @ 6.0", "Duties & Taxes"),
        ("Input Tax IGST @ 12.0", "Duties & Taxes"),

        ("Input Tax CGST @ 9.0", "Duties & Taxes"),
        ("Input Tax SGST @ 9.0", "Duties & Taxes"),
        ("Input Tax IGST @ 18.0", "Duties & Taxes"),

        ("Input Tax CGST @ 14.0", "Duties & Taxes"),
        ("Input Tax SGST @ 14.0", "Duties & Taxes"),
        ("Input Tax IGST @ 28.0", "Duties & Taxes"),

        # Output Tax
        ("Output Tax CGST @ 2.5", "Duties & Taxes"),
        ("Output Tax SGST @ 2.5", "Duties & Taxes"),
        ("Output Tax IGST @ 5.0", "Duties & Taxes"),

        ("Output Tax CGST @ 6.0", "Duties & Taxes"),
        ("Output Tax SGST @ 6.0", "Duties & Taxes"),
        ("Output Tax IGST @ 12.0", "Duties & Taxes"),

        ("Output Tax CGST @ 9.0", "Duties & Taxes"),
        ("Output Tax SGST @ 9.0", "Duties & Taxes"),
        ("Output Tax IGST @ 18.0", "Duties & Taxes"),

        ("Output Tax CGST @ 14.0", "Duties & Taxes"),
        ("Output Tax SGST @ 14.0", "Duties & Taxes"),
        ("Output Tax IGST @ 28.0", "Duties & Taxes"),
    ]

    for ledger_name, parent in ledgers:
        # Avoid duplicates
        if frappe.db.exists("Tally Account", {"account": ledger_name}):
            continue

        doc = frappe.get_doc({
            "doctype": "Tally Account",
            "account": ledger_name,
            "tally_parent": parent
            })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()



    
def create_account_parentfield():
    custom_fields = {
        "Account": [
            {
                "label": "Tally Parent Account",
                "fieldname": "custom_tally_parent_account",
                "fieldtype": "Autocomplete",
                "options": "Capital Account\nLoans (Liability)\nCurrent Liabilities\nFixed Assets\nInvestments\nCurrent Assets\nBranch / Divisions\nMisc. Expenses (Assets)\nSuspense Account\nDirect Expenses\nIndirect Expenses\nDirect Incomes\nIndirect Incomes\nSales Accounts\nPurchase Accounts\nSundry Debtors\nDuties & Taxes\nBank Accounts\nCash-in-Hand",
                "insert_after": "parent_account",
                "depends_on": "eval: doc.is_group == 0",
                "mandatory_depends_on": "eval: doc.is_group == 0",
            },
            {
                "label": "Tally",
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "insert_after": "include_in_gross"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Item": [
            {
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "label": "Tally",
                "insert_after": "total_projected_qty",
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Warehouse": [
            {
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "label": "Tally",
                "insert_after": "old_parent"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Item Group": [
            {
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "label": "Tally",
                "insert_after": "rgt"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Supplier": [
            {
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "label": "Tally",
                "insert_after": "column_break_1mqv"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Customer": [
            {
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "label": "Tally",
                "insert_after": "portal_users"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Employee": [
            {
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "label": "Tally",
                "insert_after": "connections_tab"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Sales Invoice": [
            {
                "label": "Tally",
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "insert_after": "connections_tab"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Purchase Invoice": [
            {
                "label": "Tally",
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "insert_after": "connections_tab"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status",
                "no_copy": 1
            }
        ],
        "Stock Entry": [
            {
                "label": "Tally",
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "insert_after": "tab_connections"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_tally_guid",
                "no_copy": 1
            }
        ],
        "Journal Entry": [
            {
                "label": "Tally",
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "insert_after": "amended_from"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_tally_guid",
                "no_copy": 1
            }
        ],
        "Payment Entry": [
            {
                "label": "Tally",
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "insert_after": "title"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab",
                "no_copy": 1
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id",
                "no_copy": 1
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno",
                "no_copy": 1
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_tally_guid",
                "no_copy": 1
            }
        ]
    }
    create_custom_fields(custom_fields)


def create_tally_parent_account():

    accounts = [
        {"account_name": "Debtors", "custom_tally_parent_account": "Sundry Debtors"},
        {"account_name": "Cash", "custom_tally_parent_account": "Cash-in-Hand"},
        {"account_name": "Employee Advances", "custom_tally_parent_account": "Current Assets"},
        {"account_name": "Earnest Money", "custom_tally_parent_account": "Current Assets"},
        {"account_name": "Stock In Hand", "custom_tally_parent_account": "Current Assets"},
        {"account_name": "Input Tax CGST", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Input Tax SGST", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Input Tax IGST", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Accumulated Depreciation", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Buildings", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Capital Equipments", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "CWIP Account", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Electronic Equipments", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Furnitures and Fixtures", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Office Equipments", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Plants and Machineries", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Softwares", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Temporary Opening", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Capital Stock", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Dividends Paid", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Opening Balance Equity", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Retained Earnings", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Revaluation Surplus", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Cost of Goods Sold", "custom_tally_parent_account": "Direct Expenses"},
        {"account_name": "Expenses Included In Asset Valuation", "custom_tally_parent_account": "Direct Expenses"},
        {"account_name": "Expenses Included In Valuation", "custom_tally_parent_account": "Direct Expenses"},
        {"account_name": "Stock Adjustment", "custom_tally_parent_account": "Direct Expenses"},
        {"account_name": "Customs Duty Expense", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Administrative Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Commission on Sales", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Depreciation", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Entertainment Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Exchange Gain/Loss", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Freight and Forwarding Charges", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Gain/Loss on Asset Disposal", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Impairment", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Legal Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Marketing Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Miscellaneous Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Office Maintenance Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Office Rent", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Postal Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Print and Stationery", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Round Off", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Salary", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Sales Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Telephone Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Travel Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Utility Expenses", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Write Off", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "GST Expense", "custom_tally_parent_account": "Indirect Expenses"},
        {"account_name": "Sales", "custom_tally_parent_account": "Sales Accounts"},
        {"account_name": "Service", "custom_tally_parent_account": "Sales Accounts"},
        {"account_name": "Creditors", "custom_tally_parent_account": "Sundry Creditors"},
        {"account_name": "Payroll Payable", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "TDS Payable", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Output Tax SGST", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Output Tax CGST", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Output Tax IGST", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Output Tax SGST RCM", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Output Tax CGST RCM", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Output Tax IGST RCM", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Input Tax CGST RCM", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Input Tax SGST RCM", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Input Tax IGST RCM", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Customs Duty Payable", "custom_tally_parent_account": "Duties & Taxes"},
        {"account_name": "Bank Overdraft Account", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Secured Loans", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Unsecured Loans", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Asset Received But Not Billed", "custom_tally_parent_account": "Current Liabilities"},
        {"account_name": "Stock Received But Not Billed", "custom_tally_parent_account": "Current Liabilities"}
        ]


    company_list = frappe.db.get_list('Company', fields=['name', 'abbr'])

    for company in company_list:
        for account in accounts:
            frappe.db.set_value(
                "Account",
                {"account_name": account["account_name"], "company": company["name"]},
                "custom_tally_parent_account",
                account["custom_tally_parent_account"]
            )
