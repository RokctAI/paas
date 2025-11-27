frappe.ui.form.on('Project Settings', {
    refresh(frm) {
        const doctypes = [
            'Settings',
            'Location Settings',
            'Delivery Settings',
            'Auth Settings',
            'Reservation Settings',
            'QR Code Settings',
            'Design Settings',
            'Footer Settings',
            'Social Settings',
            'App Settings',
            'Permission Settings'
        ];

        doctypes.forEach(doctype => {
            frm.add_custom_button(__(doctype), () => {
                frappe.set_route('Form', doctype);
            });
        });
    }
});
