// Copyright (c) 2022, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marup Share', {
	// refresh: function(frm) {

  customer: async function (frm) {
    const { customer } = frm.doc;
    if (customer) {
      const {
        message: { default_sales_partner, default_commission_rate } = {},
      } = await frappe.db.get_value('Customer', customer, [
        'default_sales_partner',
        'default_commission_rate',
      ]);
      frm.set_value({
        sales_partner: default_sales_partner,
        commission_rate: default_commission_rate,
      });
    } else {
      frm.set_value({
        sales_partner: null,
        commission_rate: null,
      });
    }
  },
});
