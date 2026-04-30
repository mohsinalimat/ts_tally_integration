// Copyright (c) 2024, Siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on('TS Tally Settings', {
    refresh: function (frm) {
        set_child_queries(frm);
        fetch_unmapped_accounts(frm);
        if (frm.doc.not_synced_company) {
            fetch_not_synced_data(frm);
        }
    },
    not_synced_company: function (frm) {
        if (frm.doc.not_synced_company) {
            fetch_not_synced_data(frm);
        } else {
            frm.fields_dict['not_synced_data_html'].html('');
        }
    }
});

frappe.ui.form.on('TS Tally Company', {
    company_name: function (frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'cost_center', '');
    }
});

function set_child_queries(frm) {
    frm.set_query('cost_center', 'company_table', function (doc, cdt, cdn) {
        const row = locals[cdt][cdn];

        return {
            filters: {
                company: row.company_name || ''
            }
        };
    });
}


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


function fetch_not_synced_data(frm) {
    if (!frm.fields_dict['not_synced_data_html']) return;

    frappe.call({
        method: 'ts_tally_integration.tally_integration.doctype.ts_tally_settings.ts_tally_settings.get_not_synced_data',
        args: { company: frm.doc.not_synced_company },
        freeze: true,
        freeze_message: 'Fetching not synced data...',
        callback: function (r) {
            if (!r.message || Object.keys(r.message).length === 0) {
                frm.fields_dict['not_synced_data_html'].html(
                    '<div style="text-align:center; padding:20px;"><h3>All Data is Synced</h3></div>'
                );
                return;
            }

            let html = '';
            for (let doctype in r.message) {
                let records = r.message[doctype];
                let columns = Object.keys(records[0]);

                html += `
                    <div style="margin-bottom:20px;">
                        <h4 style="background:rgb(183, 220, 255); padding:8px; margin-bottom:0;">
                            ${doctype} (${records.length} records)
                        </h4>
                        <table class="table table-bordered" style="width:100%; border-collapse:collapse;">
                            <thead>
                                <tr>
                                    <th style="border:1px solid #ddd; padding:8px;">S.No</th>
                                    ${columns.map(col => `<th style="border:1px solid #ddd; padding:8px;">${frappe.model.unscrub(col)}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                `;

                records.forEach((row, idx) => {
                    html += '<tr>';
                    html += `<td style="border:1px solid #ddd; padding:8px;">${idx + 1}</td>`;
                    columns.forEach(col => {
                        let val = row[col] || '';
                        if (col === 'name') {
                            val = `<a href="/app/${frappe.router.slug(doctype)}/${row[col]}" target="_blank">${row[col]}</a>`;
                        }
                        html += `<td style="border:1px solid #ddd; padding:8px;">${val}</td>`;
                    });
                    html += '</tr>';
                });

                html += `
                            </tbody>
                        </table>
                    </div>
                `;
            }

            frm.fields_dict['not_synced_data_html'].html(html);
        }
    });
}

