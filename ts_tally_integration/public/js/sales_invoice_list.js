frappe.listview_settings["Sales Invoice"] = frappe.listview_settings["Sales Invoice"] || {};

(function () {
	const original_onload = frappe.listview_settings["Sales Invoice"].onload;
	frappe.listview_settings["Sales Invoice"].onload = function (listview) {
		if (typeof original_onload === "function") {
			original_onload(listview);
		}
		if (ts_tally_integration && ts_tally_integration.add_bulk_remove_sync_action) {
			ts_tally_integration.add_bulk_remove_sync_action(listview);
		}
	};
})();
