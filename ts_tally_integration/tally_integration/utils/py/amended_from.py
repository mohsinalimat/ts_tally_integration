import frappe

# During Amendment, clear Tally related fields
def validate(doc, method):
    if doc.amended_from:
        doc.custom_tally_auto_id = None
        doc.custom_tally_refno = None
        doc.custom_tally_guid = None
        doc.custom_sync_time = None
