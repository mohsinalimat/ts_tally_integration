frappe.ui.form.on("Journal Entry", {
	refresh: function (frm) {
		if (ts_tally_integration && ts_tally_integration.add_remove_sync_button) {
			ts_tally_integration.add_remove_sync_button(frm);
		}
	},
});
