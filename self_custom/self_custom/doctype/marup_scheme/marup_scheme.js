// Copyright (c) 2022, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marup Scheme', {
  setup: function (frm) {
    [
      ['member_account', 'Receivable'],
      ['subscription_account', 'Income Account'],
      ['partner_account', 'Payable'],
      ['commission_account', 'Expense Account'],
    ].forEach(([field, account_type]) =>
      frm.set_query(field, (_doc, cdt, cdn) => {
        const { company } = frappe.get_doc(cdt, cdn);
        return {
          filters: {
            account_type: ['in', [account_type]],
            is_group: 0,
            company,
          },
        };
      })
    );
    frm.set_query('cost_center', (_doc, cdt, cdn) => {
      const { company } = frappe.get_doc(cdt, cdn);
      return { filters: { is_group: 0, company } };
    });
  },
  refresh: function (frm) {
    if (!frm.doc.__islocal && frm.doc.status != 'Completed') {
      frm.add_custom_button('Suspend Period', function () {
        const dialog = new frappe.ui.Dialog({
          title: 'Disable a Marup Period',
          fields: [
            {
              label: 'Marup Period',
              fieldtype: 'Link',
              fieldname: 'period',
              options: 'Marup Period',
              get_query: () => ({
                filters: { marup_scheme: frm.doc.name, disabled: 0 },
              }),
              only_select: 1,
              reqd: 1,
            },
          ],
        });

        dialog.set_primary_action('OK', async function () {
          const args = dialog.get_values();
          await frm.call('disable_period', args);
          frm.reload_doc();
          dialog.hide();
        });
        dialog.onhide = () => dialog.$wrapper.remove();
        dialog.show();
      });
    }
  },
});
