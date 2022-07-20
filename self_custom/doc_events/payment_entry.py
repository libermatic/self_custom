import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

from self_custom.doc_events.journal_entry import COMMISSION_ENTRY, SUBSCRIPTION_ENTRY
from self_custom.overrides.payment_entry import (
    set_missing_values,
    validate_reference_documents,
)


def before_validate(doc, method):
    PaymentEntry.set_missing_values = set_missing_values
    PaymentEntry.validate_reference_documents = validate_reference_documents


def validate(doc, method):
    if doc.unallocated_amount != 0.0:
        frappe.throw("There should be zero <em>Unallocated Amount</em>.")


def on_submit(doc, method):
    for item in doc.references:
        if item.reference_doctype == "Journal Entry":
            voucher_type, marup_subscription = frappe.db.get_value(
                "Journal Entry",
                item.reference_name,
                ["voucher_type", "marup_subcription"],
            )
            if marup_subscription:
                if voucher_type == SUBSCRIPTION_ENTRY:
                    frappe.db.set_value(
                        "Marup Subscription",
                        marup_subscription,
                        "subscription_status",
                        "Paid",
                    )
                elif voucher_type == COMMISSION_ENTRY:
                    frappe.db.set_value(
                        "Marup Subscription",
                        marup_subscription,
                        "commission_status",
                        "Paid",
                    )


def on_cancel(doc, method):
    for item in doc.references:
        if item.reference_doctype == "Journal Entry":
            voucher_type, marup_subscription = frappe.db.get_value(
                "Journal Entry",
                item.reference_name,
                ["voucher_type", "marup_subcription"],
            )
            if marup_subscription:
                if voucher_type == SUBSCRIPTION_ENTRY:
                    frappe.db.set_value(
                        "Marup Subscription",
                        marup_subscription,
                        "subscription_status",
                        "Billed",
                    )
                elif voucher_type == COMMISSION_ENTRY:
                    frappe.db.set_value(
                        "Marup Subscription",
                        marup_subscription,
                        "commission_status",
                        "Billed",
                    )
