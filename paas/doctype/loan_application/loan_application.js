// Copyright (c) 2025 ROKCT INTELLIGENCE (PTY) LTD
// For license information, please see license.txt

frappe.ui.form.on("Loan Application", {
	refresh(frm) {
        if (!frm.is_new() && frm.doc.status === "Pending Review") {
            frm.add_custom_button(__("Generate Scorecard"), function() {
                frappe.call({
                    method: "rokct.paas.api.generate_scorecard",
                    args: {
                        loan_application: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
	},
});
