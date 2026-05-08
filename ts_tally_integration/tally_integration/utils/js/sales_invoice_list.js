frappe.listview_settings["Sales Invoice"] = frappe.listview_settings["Sales Invoice"] || {};

(function () {
	const original_onload = frappe.listview_settings["Sales Invoice"].onload;
	frappe.listview_settings["Sales Invoice"].onload = function (listview) {
		if (typeof original_onload === "function") {
			original_onload(listview);
		}

		if (frappe.session.user !== "Administrator") return;

		listview.page.add_actions_menu_item(
			__("Set Manual Tally Sync Data"),
			function () {
				const selected = listview.get_checked_items();
				if (!selected || !selected.length) {
					frappe.msgprint(__("Please select at least one record"));
					return;
				}
				const names = selected.map((d) => d.name);

				frappe.confirm(
					__("Set Tally sync data manually for {0} selected {1}?", [
						names.length,
						__(listview.doctype),
					]),
					function () {
						frappe.call({
							method: "ts_tally_integration.tally_integration.utils.py.remove_sync_data.bulk_manual_sync_data",
							args: { doctype: listview.doctype, names: names },
							freeze: true,
							freeze_message: __("Setting Tally sync data..."),
							callback: function (r) {
								const msg = r.message || {};
								const updated = (msg.updated || []).length;
								const failed = (msg.failed || []).length;
								if (updated) {
									frappe.show_alert({
										message: __("Set manual sync data for {0} record(s)", [updated]),
										indicator: "green",
									});
								}
								if (failed) {
									frappe.show_alert({
										message: __("Failed for {0} record(s)", [failed]),
										indicator: "red",
									});
								}
								listview.refresh();
							},
						});
					}
				);
			},
			false
		);

		listview.page.add_actions_menu_item(
			__("Remove Tally Sync Data"),
			function () {
				const selected = listview.get_checked_items();
				if (!selected || !selected.length) {
					frappe.msgprint(__("Please select at least one record"));
					return;
				}
				const names = selected.map((d) => d.name);

				frappe.confirm(
					__("Remove Tally sync data from {0} selected {1}?", [
						names.length,
						__(listview.doctype),
					]),
					function () {
						frappe.call({
							method: "ts_tally_integration.tally_integration.utils.py.remove_sync_data.bulk_remove_sync_data",
							args: { doctype: listview.doctype, names: names },
							freeze: true,
							freeze_message: __("Removing Tally sync data..."),
							callback: function (r) {
								const msg = r.message || {};
								const cleared = (msg.cleared || []).length;
								const failed = (msg.failed || []).length;
								if (cleared) {
									frappe.show_alert({
										message: __("Removed sync data from {0} record(s)", [cleared]),
										indicator: "green",
									});
								}
								if (failed) {
									frappe.show_alert({
										message: __("Failed for {0} record(s)", [failed]),
										indicator: "red",
									});
								}
								listview.refresh();
							},
						});
					}
				);
			},
			false
		);
	};
})();
