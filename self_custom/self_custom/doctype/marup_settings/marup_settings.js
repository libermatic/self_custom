// Copyright (c) 2022, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marup Settings', {
  setup: function (frm) {
    [
      ['default_member_account', 'Receivable'],
      ['default_subscription_account', 'Income Account'],
      ['default_partner_account', 'Payable'],
      ['default_commission_account', 'Expense Account'],
    ].forEach(([field, account_type]) =>
      frm.set_query(field, 'accounts', (_doc, cdt, cdn) => {
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
  },
});
