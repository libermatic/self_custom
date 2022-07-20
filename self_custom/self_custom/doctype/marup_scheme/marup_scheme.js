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
});
