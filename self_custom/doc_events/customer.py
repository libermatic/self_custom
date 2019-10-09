# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, first, excepts, get


def on_update(doc, method):
    if doc.customer_primary_contact and not doc.mobile_no:
        get_number = compose(
            partial(get, "phone", default=None),
            excepts(StopIteration, first, lambda __: {}),
            frappe.db.sql,
        )
        mobile_no = get_number(
            """
                SELECT phone FROM `tabContact Phone`
                WHERE parent = %(parent)s AND is_primary_mobile_no = 1
                LIMIT 1
            """,
            values={"parent": doc.customer_primary_contact},
            as_dict=1,
        )
        frappe.db.set_value("Customer", doc.name, "mobile_no", mobile_no)
        doc.reload()
