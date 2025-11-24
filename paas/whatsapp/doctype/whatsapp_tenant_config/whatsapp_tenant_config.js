// Copyright (c) 2025, ROKCT and contributors
// For license information, please see license.txt

frappe.ui.form.on('WhatsApp Tenant Config', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Provision Flow'), function () {
                frappe.call({
                    method: 'paas.paas.whatsapp.api.flow_management.create_flow',
                    freeze: true,
                    freeze_message: 'Creating Flow on Meta...',
                    callback: function (r) {
                        if (r.message && r.message.status === 'success') {
                            frappe.msgprint(r.message.message);
                            frm.reload_doc();
                        }
                    }
                });
            });

            if (!frm.doc.private_key) {
                frm.add_custom_button(__('Generate Encryption Keys'), function () {
                    frappe.confirm('This will generate a new Private/Public Key pair. If you have already uploaded a key to Meta, this will invalidate it. Continue?', () => {
                        frm.call({
                            method: 'generate_keys',
                            doc: frm.doc,
                            callback: function (r) {
                                frm.reload_doc();
                                frappe.msgprint("Keys generated! Copy the Public Key to Meta.");
                            }
                        });
                    });
                });
            }
        }
    }
});
