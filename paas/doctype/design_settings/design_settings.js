frappe.ui.form.on('Design Settings', {
    refresh(frm) {
        frm.trigger('render_ui_selector');
    },

    render_ui_selector(frm) {
        const wrapper = frm.get_field('ui_selector').$wrapper;
        wrapper.empty();

        const ui_types = [
            { value: '1', img: '/assets/rokct/images/ui-type1.png', title: 'View 1' },
            { value: '2', img: '/assets/rokct/images/ui-type2.png', title: 'View 2' },
            { value: '3', img: '/assets/rokct/images/ui-type3.png', title: 'View 3' },
            { value: '4', img: '/assets/rokct/images/ui-type4.png', title: 'View 4' }
        ];

        let html = `<div style="display: flex; gap: 20px; flex-wrap: wrap;">`;

        ui_types.forEach(type => {
            const is_selected = frm.doc.ui_type == type.value;
            const border = is_selected ? '3px solid var(--primary)' : '1px solid var(--border-color)';

            html += `
                <div class="ui-type-card" data-value="${type.value}" style="
                    cursor: pointer;
                    border: ${border};
                    border-radius: 8px;
                    padding: 10px;
                    width: 200px;
                    text-align: center;
                    transition: all 0.2s;
                ">
                    <img src="${type.img}" style="width: 100%; border-radius: 4px; margin-bottom: 10px;">
                    <div style="font-weight: bold;">${type.title}</div>
                    <input type="radio" name="ui_type_radio" ${is_selected ? 'checked' : ''} style="pointer-events: none;">
                </div>
            `;
        });

        html += `</div>`;

        wrapper.html(html);

        wrapper.find('.ui-type-card').on('click', function() {
            const value = $(this).data('value').toString();
            frm.set_value('ui_type', value);
        });
    },

    ui_type(frm) {
        frm.trigger('render_ui_selector');
    }
});
