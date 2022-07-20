from typing import Tuple
import frappe


from self_custom.doc_events.journal_entry import COMMISSION_ENTRY, SUBSCRIPTION_ENTRY
from self_custom.self_custom.doctype.marup_subscription.marup_subscription import (
    make_journal_entry,
)


@frappe.whitelist()
def make_subscription_entry(source_name, target_doc=None):
    return _make_journal_entry(SUBSCRIPTION_ENTRY, source_name)


@frappe.whitelist()
def make_commission_entry(source_name, target_doc=None):
    return _make_journal_entry(COMMISSION_ENTRY, source_name)


def _make_journal_entry(voucher_type: str, source_name):
    subscription = frappe.get_doc("Marup Subscription", source_name)

    if not subscription or subscription.docstatus != 1:
        frappe.throw("Invalid <strong>Marup Subscription</Marup>.")

    share = frappe.get_doc("Marup Share", subscription.marup_share)
    scheme = frappe.get_doc("Marup Scheme", subscription.marup_scheme)
    settings = frappe.db.get_value(
        "SELF Default Account", filters={"company": scheme.company}, fieldname="*"
    )
    company = frappe.get_doc("Company", scheme.company)

    return make_journal_entry(
        voucher_type, subscription, share, scheme, settings, company
    )
