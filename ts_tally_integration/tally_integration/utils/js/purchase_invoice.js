frappe.ui.form.on("Purchase Invoice", {
	refresh: function (frm) {
		if (frm.is_new()) return;
		if (frappe.session.user !== "Administrator") return;

		const has_sync_data =
			frm.doc.custom_tally_auto_id ||
			frm.doc.custom_tally_refno ||
			frm.doc.custom_tally_guid ||
			frm.doc.custom_sync_time;

		if (!has_sync_data) return;

		frm.add_custom_button(
			__("Remove Sync Data"),
			function () {
				frappe.confirm(
					__("Are you sure you want to remove the Tally sync data from this {0}?", [
						__(frm.doctype),
					]),
					function () {
						frappe.call({
							method: "ts_tally_integration.tally_integration.utils.py.remove_sync_data.remove_sync_data",
							args: { doctype: frm.doctype, name: frm.doc.name },
							freeze: true,
							freeze_message: __("Removing Tally sync data..."),
							callback: function (r) {
								if (r.message && r.message.status === "success") {
									frappe.show_alert({
										message: __("Tally sync data removed"),
										indicator: "green",
									});
									frm.reload_doc();
								}
							},
						});
					}
				);
			},
			__("Tally")
		);
	},
});
