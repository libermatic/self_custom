import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

from self_custom.overrides.payment_entry import (
    set_missing_values,
    validate_reference_documents,
)


def before_validate(doc, method):
    PaymentEntry.set_missing_values = set_missing_values
    PaymentEntry.validate_reference_documents = validate_reference_documents
