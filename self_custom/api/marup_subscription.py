import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account


from self_custom.doc_events.journal_entry import COMMISSION_ENTRY, SUBSCRIPTION_ENTRY
from self_custom.self_custom.doctype.marup_subscription.marup_subscription import (
    make_journal_entry,
)
from self_custom.overrides.payment_entry import override_payment_entry


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


@frappe.whitelist()
def make_subscription_payment(source_name, target_doc=None):
    je = frappe.db.exists(
        "Journal Entry",
        {
            "docstatus": 1,
            "voucher_type": SUBSCRIPTION_ENTRY,
            "marup_subscription": source_name,
        },
    )

    if not je:
        frappe.throw("Subscription <strong>Journal Entry</strong> does not exist.")

    return _make_payment_entry(je)


@frappe.whitelist()
def make_commission_payment(source_name, target_doc=None):
    je = frappe.db.exists(
        "Journal Entry",
        {
            "docstatus": 1,
            "voucher_type": COMMISSION_ENTRY,
            "marup_subscription": source_name,
        },
    )

    if not je:
        frappe.throw("Commission <strong>Journal Entry</strong> does not exist.")

    return _make_payment_entry(je)


@override_payment_entry
def _make_payment_entry(source_name):
    def get_amount_fields(source):
        if source.voucher_type == SUBSCRIPTION_ENTRY:
            return "debit_in_account_currency", "paid_from", "paid_to"

        if source.voucher_type == COMMISSION_ENTRY:
            return "credit_in_account_currency", "paid_to", "paid_from"

    def get_payment_type(source):
        if source.voucher_type == SUBSCRIPTION_ENTRY:
            return "Receive"

        if source.voucher_type == COMMISSION_ENTRY:
            return "Pay"

    def get_party_row(source):
        for row in source.accounts:
            if row.party_type and row.party:
                return row

    def postprocess(source, target):
        party_row = get_party_row(source)
        amount_field, account_field, bank_field = get_amount_fields(source)
        amount = party_row.get(amount_field)

        mop = "Cash"
        bank = get_bank_cash_account(mop, source.company)

        target.update(
            {
                "payment_type": get_payment_type(source),
                "mode_of_payment": mop,
                "party_type": party_row.party_type,
                "party": party_row.party,
                account_field: party_row.account,
                bank_field: bank.get("account"),
                "paid_amount": amount,
                "received_amount": amount,
                "marup_scheme": party_row.marup_scheme,
            }
        )
        target.append(
            "references",
            {
                "reference_doctype": "Journal Entry",
                "reference_name": source.name,
                "total_amount": amount,
                "outstanding_amount": amount,
                "allocated_amount": amount,
            },
        )

        target.setup_party_account_field()
        target.set_missing_values()

    return frappe.model.mapper.get_mapped_doc(
        "Journal Entry",
        source_name,
        {
            "Journal Entry": {
                "doctype": "Payment Entry",
                "field_map": {"company": "company"},
            }
        },
        None,
        postprocess,
    )
