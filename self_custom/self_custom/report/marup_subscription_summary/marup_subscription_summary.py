# Copyright (c) 2022, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder.functions import Count, Sum


def execute(filters=None):
    return _get_columns(filters), _get_data(filters)


def _get_columns(filters):
    common = [
        {"fieldtype": "Int", "fieldname": "count", "label": "Count", "width": 80},
        {
            "fieldtype": "Currency",
            "fieldname": "total_amount",
            "label": "Total Amount",
            "width": 120,
        },
        {
            "fieldtype": "Currency",
            "fieldname": "outstanding_amount",
            "label": "Outstanding",
            "width": 120,
        },
    ]

    customer = [
        {
            "fieldtype": "Link",
            "fieldname": "customer",
            "label": "Customer",
            "options": "Customer",
            "width": 120,
        },
        {
            "fieldtype": "Data",
            "fieldname": "customer_name",
            "label": "Customer Name",
            "width": 150,
        },
    ]
    sales_partner = [
        {
            "fieldtype": "Link",
            "fieldname": "sales_partner",
            "label": "Sales Partner",
            "options": "Sales Partner",
            "width": 120,
        },
        {
            "fieldtype": "Data",
            "fieldname": "sales_partner_name",
            "label": "Partner Name",
            "width": 150,
        },
    ]

    if filters.group_by == "Customer":
        return customer + common

    if filters.group_by == "Sales Partner":
        return sales_partner + common

    return (
        [
            {
                "fieldtype": "Link",
                "fieldname": "marup_share",
                "label": "Marup Share",
                "options": "Marup Share",
                "width": 120,
            }
        ]
        + customer
        + sales_partner
        + common
    )


def _get_data(filters):
    MarupShare = frappe.qb.DocType("Marup Share")
    MarupSubscription = frappe.qb.DocType("Marup Subscription")
    JournalEntry = frappe.qb.DocType("Journal Entry")
    PaymentEntryReference = frappe.qb.DocType("Payment Entry Reference")

    share_query = (
        frappe.qb.from_(MarupShare)
        .left_join(MarupSubscription)
        .on(MarupSubscription.marup_share == MarupShare.name)
        .left_join(JournalEntry)
        .on(
            (JournalEntry.docstatus == 1)
            & (JournalEntry.marup_subscription == MarupSubscription.name)
        )
        .left_join(PaymentEntryReference)
        .on(
            (PaymentEntryReference.docstatus == 1)
            & (PaymentEntryReference.reference_doctype == "Journal Entry")
            & (PaymentEntryReference.reference_name == JournalEntry.name)
        )
        .where(MarupShare.marup_scheme == filters.marup_scheme)
        .select(
            MarupShare.name.as_("marup_share"),
            MarupShare.customer,
            MarupShare.customer_name,
            MarupShare.sales_partner,
            MarupShare.sales_partner_name,
            Count(MarupSubscription.name).as_("count"),
            Sum(JournalEntry.total_debit).as_("total_amount"),
            Sum(PaymentEntryReference.allocated_amount).as_("paid_amount"),
        )
    )

    if filters.group_by == "Customer":
        share_query = share_query.where(
            JournalEntry.voucher_type == "Subscription Entry"
        ).groupby(MarupShare.customer)
    elif filters.group_by == "Sales Partner":
        share_query = share_query.where(
            JournalEntry.voucher_type == "Commission Entry"
        ).groupby(MarupShare.sales_partner)
    else:
        share_query = share_query.where(
            JournalEntry.voucher_type == "Subscription Entry"
        ).groupby(MarupShare.name)

    result = share_query.run(as_dict=1, debug=1)

    return [{**x, "outstanding_amount": _get_oustanding(x)} for x in result]


def _get_oustanding(row):
    total_amount = row.get("total_amount") or 0
    paid_amount = row.get("paid_amount") or 0
    return total_amount - paid_amount
