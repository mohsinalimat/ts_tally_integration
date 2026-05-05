frappe.ui.form.on("Purchase Invoice", {
	refresh: function (frm) {
		if (ts_tally_integration && ts_tally_integration.add_remove_sync_button) {
			ts_tally_integration.add_remove_sync_button(frm);
		}
	},
});
