// Copyright (c) 2024, Siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on('TS Tally Settings', {
    refresh: function (frm) {
        set_child_queries(frm);
        fetch_unmapped_accounts(frm);
        fetch_sync_dashboard(frm);
        if (frm.doc.not_synced_company) {
            set_cost_center_for_company(frm);
            fetch_not_synced_data(frm);
        }
    },
    not_synced_company: function (frm) {
        if (frm.doc.not_synced_company) {
            set_cost_center_for_company(frm);
            fetch_not_synced_data(frm);
        } else {
            frm.set_value('not_synced_cost_center', '');
            frm.fields_dict['not_synced_data_html'].html('');
        }
    }
});

function set_cost_center_for_company(frm) {
    const row = (frm.doc.company_table || []).find(
        r => r.company_name === frm.doc.not_synced_company
    );
    frm.set_value('not_synced_cost_center', (row && row.cost_center) || '');
}

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


function fetch_sync_dashboard(frm) {
    if (!frm.fields_dict['sync_dashboard_html']) return;

    frm.fields_dict['sync_dashboard_html'].html(
        '<div style="text-align:center; padding:20px; color:#888;">Loading sync dashboard...</div>'
    );

    frappe.call({
        method: 'ts_tally_integration.tally_integration.doctype.ts_tally_settings.ts_tally_settings.get_sync_dashboard_data',
        callback: function (r) {
            if (!r.message) return;
            frm.fields_dict['sync_dashboard_html'].html(render_sync_dashboard(r.message));
        }
    });
}

function render_sync_dashboard(data) {
    const refresh_btn = `
        <div style="text-align:right; margin-bottom:10px;">
            <button class="btn btn-default btn-sm" onclick="cur_frm && cur_frm.trigger('refresh')">
                Refresh
            </button>
        </div>
    `;

    let html = refresh_btn;

    if (data.global_masters && data.global_masters.length) {
        html += render_dashboard_section('Global Masters (Company Independent)', data.global_masters, true);
    }

    (data.companies || []).forEach(c => {
        const meta = [];
        if (c.sync_from) meta.push(`Sync From: <b>${frappe.datetime.str_to_user(c.sync_from)}</b>`);
        if (c.cost_center) meta.push(`Cost Center: <b>${frappe.utils.escape_html(c.cost_center)}</b>`);
        const meta_html = meta.length
            ? `<div style="margin:4px 0 8px; color:#666; font-size:12px;">${meta.join(' &nbsp;|&nbsp; ')}</div>`
            : '';

        html += `
            <div style="margin-top:24px; padding:12px; border:1px solid #e2e6ea; border-radius:6px;">
                <h3 style="margin:0;">${frappe.utils.escape_html(c.company)}</h3>
                ${meta_html}
        `;
        if (c.masters && c.masters.length) {
            html += render_dashboard_section('Master Data', c.masters, true);
        }
        if (c.vouchers && c.vouchers.length) {
            html += render_dashboard_section('Voucher Data', c.vouchers, false);
        }
        html += `</div>`;
    });

    return html;
}

function render_dashboard_section(title, rows, show_failure) {
    const failure_header = show_failure
        ? `<th style="border:1px solid #ddd; padding:8px; text-align:left;">Last Failure</th>`
        : '';

    let body = '';
    rows.forEach(r => {
        const total = (r.pending || 0) + (r.synced || 0);
        const pending_color = (r.pending && r.pending > 0) ? '#c0392b' : '#2c3e50';
        const last_sync = r.last_sync ? frappe.datetime.str_to_user(r.last_sync) : '—';

        let last_failure = '—';
        if (show_failure && r.last_failure) {
            const slug = frappe.router.slug(r.doctype);
            const name = frappe.utils.escape_html(r.last_failure.name || '');
            const t = r.last_failure.time ? frappe.datetime.str_to_user(r.last_failure.time) : '';
            last_failure = `<a href="/app/${slug}/${encodeURIComponent(r.last_failure.name)}" target="_blank">${name}</a>`
                + (t ? ` <span style="color:#888;">(${t})</span>` : '');
        }

        body += `
            <tr>
                <td style="border:1px solid #ddd; padding:8px;">${frappe.utils.escape_html(r.doctype)}</td>
                <td style="border:1px solid #ddd; padding:8px; text-align:right; color:${pending_color}; font-weight:600;">${r.pending || 0}</td>
                <td style="border:1px solid #ddd; padding:8px; text-align:right; color:#27ae60; font-weight:600;">${r.synced || 0}</td>
                <td style="border:1px solid #ddd; padding:8px; text-align:right; color:#666;">${total}</td>
                <td style="border:1px solid #ddd; padding:8px;">${last_sync}</td>
                ${show_failure ? `<td style="border:1px solid #ddd; padding:8px;">${last_failure}</td>` : ''}
            </tr>
        `;
    });

    return `
        <h4 style="background:rgb(183, 220, 255); padding:8px; margin: 12px 0 0;">${title}</h4>
        <table class="table table-bordered" style="width:100%; border-collapse:collapse; margin:0;">
            <thead>
                <tr>
                    <th style="border:1px solid #ddd; padding:8px; text-align:left;">Doctype</th>
                    <th style="border:1px solid #ddd; padding:8px; text-align:right;">Pending</th>
                    <th style="border:1px solid #ddd; padding:8px; text-align:right;">Synced</th>
                    <th style="border:1px solid #ddd; padding:8px; text-align:right;">Total</th>
                    <th style="border:1px solid #ddd; padding:8px; text-align:left;">Last Sync</th>
                    ${failure_header}
                </tr>
            </thead>
            <tbody>${body}</tbody>
        </table>
    `;
}

