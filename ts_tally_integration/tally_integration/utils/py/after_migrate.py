from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_migrate():
    custom_fields = {
        "Item": [
            {
                "fieldname": "tally_tab",
                "fieldtype": "Tab Break",
                "label": "Tally",
                "insert_after": "total_projected_qty"
            },
            {
                "label": "Tally Auto ID",
                "fieldname": "custom_tally_auto_id",
                "fieldtype": "Data",
                "insert_after": "tally_tab"
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status"
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
                "insert_after": "tally_tab"
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status"
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
                "insert_after": "tally_tab"
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status"
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
                "insert_after": "tally_tab"
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status"
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
                "insert_after": "tally_tab"
            },
            {
                "label": "Status",
                "fieldname": "custom_status",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status"
            }
        ],
        "Sales Invoice": [
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
                "insert_after": "tally_tab"
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status"
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
                "insert_after": "tally_tab"
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_status"
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
                "insert_after": "tally_tab"
            },
            {
                "label": "Tally REFNO",
                "fieldname": "custom_tally_refno",
                "fieldtype": "Data",
                "insert_after": "custom_tally_auto_id"
            },
            {
                "label": "Tally GUID",
                "fieldname": "custom_tally_guid",
                "fieldtype": "Data",
                "insert_after": "custom_tally_refno"
            },
            {
                "label": "Sync Time",
                "fieldname": "custom_sync_time",
                "fieldtype": "Datetime",
                "insert_after": "custom_tally_guid"
            }
        ]
    }

    create_custom_fields(custom_fields)


