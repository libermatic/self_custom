frappe.listview_settings['Marup Subscription'] = {
  add_fields: ['subscription_status', 'commission_status'],
  get_indicator({ subscription_status, commission_status }) {
    if (subscription_status === 'Paid' && commission_status === 'Paid') {
      return [
        'Paid',
        'green',
        'subscription_status,=,Paid|commission_status,=,Paid',
      ];
    }

    if (subscription_status === 'Billed' && commission_status === 'Billed') {
      return [
        'Unpaid',
        'red',
        'subscription_status,=,Billed|commission_status,=,Billed',
      ];
    }

    if (subscription_status === 'Billed') {
      return ['Subscription Unpaid', 'orange', 'subscription_status,=,Billed'];
    }

    if (commission_status === 'Billed') {
      return ['Commission Unpaid', 'yellow', 'commission_status,=,Billed'];
    }

    return [
      'Unbilled',
      'darkgrey',
      'subscription_status,is,not set|commission_status,is,not set',
    ];
  },
};
