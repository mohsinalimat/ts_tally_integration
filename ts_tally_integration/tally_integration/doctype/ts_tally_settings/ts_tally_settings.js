// Copyright (c) 2024, Siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on('TS Tally Settings', {
    refresh: function (frm) {
        fetch_unmapped_accounts(frm);
    }
});


function fetch_unmapped_accounts(frm) {
    if (frm.fields_dict['unmapped_accounts']) {
        frappe.call({
            method: 'ts_tally_integration.tally_integration.doctype.ts_tally_settings.ts_tally_settings.get_unmapped_accounts',
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    let table = `
                        <h3 style="text-align: center">UNMAPPED ACCOUNTS</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <th>
                                <tr>
                                    <th style="border: 1px solid #ddd; padding: 8px; background:rgb(183, 220, 255);">S.No</th>
                                    <th style="border: 1px solid #ddd; padding: 8px; background:rgb(183, 220, 255);">Account Name</th>
                                    <th style="border: 1px solid #ddd; padding: 8px; background:rgb(183, 220, 255);">Company</th>
                                </tr>
                            </th>
                    `;

                    r.message.forEach((account, index) => {
                        table += `
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 8px;">${index + 1}</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">${account.name}</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">${account.company}</td>
                            </tr>
                        `;
                    });


                    frm.fields_dict['unmapped_accounts'].html(table);
                } else {
                    frm.fields_dict['unmapped_accounts'].html("<h3>ALL ACCOUNTS MAPPED</h3>");
                }
            }
        });
    }
}


