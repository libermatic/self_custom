import frappe

from self_custom.doc_events.journal_entry import COMMISSION_ENTRY, SUBSCRIPTION_ENTRY
from self_custom.overrides.payment_entry import override_payment_entry


@override_payment_entry
def before_validate(doc, method):
    pass


def validate(doc, method):
    if doc.unallocated_amount != 0.0:
        frappe.throw("There should be zero <em>Unallocated Amount</em>.")


def on_submit(doc, method):
    for item in doc.references:
        if item.reference_doctype == "Journal Entry":
            voucher_type, marup_subscription = frappe.db.get_value(
                "Journal Entry",
                item.reference_name,
                ["voucher_type", "marup_subscription"],
            )
            if marup_subscription:
                msdoc = frappe.get_doc("Marup Subscription", marup_subscription)
                if voucher_type == SUBSCRIPTION_ENTRY:
                    msdoc.set_subscription_status("Paid")
                elif voucher_type == COMMISSION_ENTRY:
                    msdoc.set_commission_status("Paid")


def on_cancel(doc, method):
    for item in doc.references:
        if item.reference_doctype == "Journal Entry":
            voucher_type, marup_subscription = frappe.db.get_value(
                "Journal Entry",
                item.reference_name,
                ["voucher_type", "marup_subscription"],
            )
            if marup_subscription:
                msdoc = frappe.get_doc("Marup Subscription", marup_subscription)
                if voucher_type == SUBSCRIPTION_ENTRY:
                    msdoc.set_subscription_status("Billed")
                elif voucher_type == COMMISSION_ENTRY:
                    msdoc.set_commission_status("Billed")
