// Copyright (c) 2022, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Marup Subscription Summary'] = {
  filters: [
    {
      fieldname: 'marup_scheme',
      label: 'Marup Scheme',
      fieldtype: 'Link',
      options: 'Marup Scheme',
      reqd: 1,
    },
    {
      fieldname: 'group_by',
      label: 'Group By',
      fieldtype: 'Select',
      options: '\nCustomer\nSales Partner',
    },
  ],
};
