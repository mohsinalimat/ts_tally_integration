import frappe
# from ts_tally_integration.tally_integration.utils.py.user import user_creation
# from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


# def after_install():
#     print("Creating Tally User...")
#     user_creation()
#     print("Tally User Created")

#     create_account_parentfield()

# def create_account_parentfield():
#     custom_fields = {
#         "Account": [
#             {
#                 "label": "Tally Parent Account",
#                 "fieldname": "custom_tally_parent_account",
#                 "fieldtype": "Autocomplete",
#                 "options":"Sundry Debtors\nDuties & Taxes\nDirect Expenses\nSales Accounts\nPurchase Accounts\nIndirect Expenses\nBank Accounts\nCash-in-Hand",
#                 "insert_after": "parent_account",
#                 "depends_on": "eval: doc.is_group == 0",
#                 "mandatory_depends_on": "eval: doc.is_group == 0",
#             }
#         ]
#     }
#     create_custom_fields(custom_fields=custom_fields)


# def create_tally_parent_account():
company_list = frappe.db.get_all('Company', fields=['name', 'abbr'])
for company in company_list:

    accounts = [
                {"account_name": "Debtors", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Cash", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Employee Advances", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Earnest Money", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Stock In Hand", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Input Tax CGST", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Input Tax SGST", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Input Tax IGST", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Accumulated Depreciation", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Buildings", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Capital Equipments", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "CWIP Account", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Electronic Equipments", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Furnitures and Fixtures", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Office Equipments", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Plants and Machineries", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Softwares", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Temporary Opening", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Capital Stock", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Dividends Paid", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Opening Balance Equity", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Retained Earnings", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Revaluation Surplus", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Cost of Goods Sold", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Expenses Included In Asset Valuation", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Expenses Included In Valuation", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Stock Adjustment", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Customs Duty Expense", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Administrative Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Commission on Sales", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Depreciation", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Entertainment Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Exchange Gain/Loss", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Freight and Forwarding Charges", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Gain/Loss on Asset Disposal", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Impairment", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Legal Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Marketing Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Miscellaneous Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Office Maintenance Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Office Rent", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Postal Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Print and Stationery", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Round Off", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Salary", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Sales Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Telephone Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Travel Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Utility Expenses", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Write Off", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "GST Expense", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Sales", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Service", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Creditors", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Payroll Payable", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "TDS Payable", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Output Tax SGST", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Output Tax CGST", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Output Tax IGST", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Output Tax SGST RCM", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Output Tax CGST RCM", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Output Tax IGST RCM", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Input Tax CGST RCM", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Input Tax SGST RCM", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Input Tax IGST RCM", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Customs Duty Payable", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Bank Overdraft Account", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Secured Loans", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Unsecured Loans", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Asset Received But Not Billed", "custom_tally_parent_account": "Sundry Debtors"},
                {"account_name": "Stock Received But Not Billed", "custom_tally_parent_account": "Sundry Debtors"}
            ]

    for account in accounts:
        print('AAAAAAAAAAAAAAAA', account)