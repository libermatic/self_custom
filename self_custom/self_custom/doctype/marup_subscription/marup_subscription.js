// Copyright (c) 2022, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marup Subscription', {
  setup: function (frm) {
    frm.set_query('marup_period', (doc) => ({
      filters: { marup_scheme: doc.marup_scheme, disabled: 0 },
    }));
  },
  refresh: function (frm) {
    if (frm.doc.docstatus === 1) {
      if (!frm.doc.subscription_status) {
        frm.add_custom_button(
          'Subscription Journal Entry',
          () => {
            frappe.model.open_mapped_doc({
              method:
                'self_custom.api.marup_subscription.make_subscription_entry',
              frm,
            });
          },
          'Create'
        );
      } else if (frm.doc.subscription_status === 'Billed') {
        frm.add_custom_button(
          'Subscription Payment',
          () => {
            frappe.model.open_mapped_doc({
              method:
                'self_custom.api.marup_subscription.make_subscription_payment',
              frm,
            });
          },
          'Create'
        );
      }
      if (!frm.doc.commission_status) {
        frm.add_custom_button(
          'Commission Journal Entry',
          () => {
            frappe.model.open_mapped_doc({
              method:
                'self_custom.api.marup_subscription.make_commission_entry',
              frm,
            });
          },
          'Create'
        );
      } else if (frm.doc.commission_status === 'Billed') {
        frm.add_custom_button(
          'Commission Payment',
          () => {
            frappe.model.open_mapped_doc({
              method:
                'self_custom.api.marup_subscription.make_commission_payment',
              frm,
            });
          },
          'Create'
        );
      }
    }
  },
});
