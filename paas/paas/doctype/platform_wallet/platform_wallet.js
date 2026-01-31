// Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD

frappe.ui.form.on('Platform Wallet', {
    refresh: function(frm) {
        frappe.db.get_single_value("Permission Settings", "enable_paas_lending")
            .then(value => {
                if (!value) {
                    frm.disable_save();
                    frm.set_intro(__("Lending feature is disabled. You cannot access the wallet."), "red");
                    frm.toggle_display("current_balance", false);
                    frm.toggle_display("withdraw_amount", false);
                    frm.toggle_display("request_payout", false);
                } else {
                    if (frm.doc.__onload && frm.doc.__onload.current_balance !== undefined) {
                        frm.set_value('current_balance', frm.doc.__onload.current_balance);
                    }
                }
            });
    },
    request_payout: function(frm) {
        if (!frm.doc.withdraw_amount || frm.doc.withdraw_amount <= 0) {
            frappe.msgprint(__("Please enter a valid withdraw amount."));
            return;
        }

        frappe.call({
            method: "request_payout",
            doc: frm.doc,
            args: {
                amount: frm.doc.withdraw_amount
            },
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint(__("Payout requested successfully."));
                    frm.set_value('withdraw_amount', 0);
                    frm.reload_doc();
                }
            }
        });
    }
});
