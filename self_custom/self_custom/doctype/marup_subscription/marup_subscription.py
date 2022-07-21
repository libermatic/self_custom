# Copyright (c) 2022, Libermatic and contributors
# For license information, please see license.txt

from typing import Tuple
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

from self_custom.doc_events.journal_entry import (
    COMMISSION_ENTRY,
    MARUP_VOUCHER_TYPES,
    SUBSCRIPTION_ENTRY,
)


class MarupSubscription(Document):
    def validate(self):
        disabled = frappe.db.get_value("Marup Period", self.marup_period, "disabled")
        if disabled:
            frappe.throw(
                "Cannot create subscription for a <em>disabled</em> "
                "<strong>Marup Period</strong>"
            )

        if frappe.db.exists(
            "Marup Subscription", {"marup_period": self.marup_period, "docstatus": 1}
        ):
            frappe.throw(
                "<strong>Marup Subscription</strong> already exists for this "
                "<strong>Marup Period</strong>."
            )

        period_scheme = frappe.db.get_value(
            "Marup Period", self.marup_period, "marup_scheme"
        )
        share_scheme = frappe.db.get_value(
            "Marup Share", self.marup_share, "marup_scheme"
        )
        if period_scheme != share_scheme:
            frappe.throw(
                "Mismatched <strong>Marup Scheme</strong> between the ones in the "
                "selected <strong>Marup Share</strong> and "
                "<strong>Marup Period</strong>."
            )

    def on_submit(self):
        share = frappe.get_doc("Marup Share", self.marup_share)
        scheme = frappe.get_doc("Marup Scheme", self.marup_scheme)
        settings = frappe.db.get_value(
            "Marup Default", filters={"company": scheme.company}, fieldname="*"
        )
        company = frappe.get_doc("Company", scheme.company)
        args = [self, share, scheme, settings, company]

        subscription_entry = make_journal_entry(*[SUBSCRIPTION_ENTRY, *args])
        subscription_entry.flags.ignore_permissions = True
        subscription_entry.insert()
        subscription_entry.submit()

        commission_entry = make_journal_entry(*[COMMISSION_ENTRY, *args])
        commission_entry.flags.ignore_permissions = True
        commission_entry.insert()
        commission_entry.submit()

    def before_cancel(self):
        for (name,) in frappe.get_all(
            "Journal Entry",
            filters={
                "voucher_type": ("in", MARUP_VOUCHER_TYPES),
                "docstatus": 1,
                "marup_subscription": self.name,
            },
            as_list=1,
        ):
            je = frappe.get_doc("Journal Entry", name)
            je.flags.ignore_permissions = True
            je.cancel()

    def set_subscription_status(self, status):
        self.flags.ignore_validate_update_after_submit = True
        self.subscription_status = status
        self.save()

    def set_commission_status(self, status):
        self.flags.ignore_validate_update_after_submit = True
        self.commission_status = status
        self.save()


def make_journal_entry(
    voucher_type: str, subscription, share, scheme, settings, company
):
    def get_accounts() -> Tuple[str, str]:
        if voucher_type == SUBSCRIPTION_ENTRY:
            return (
                scheme.member_account
                or settings.default_member_account
                or company.default_receivable_account,
                scheme.subscription_account
                or settings.default_subscription_account
                or company.default_income_account,
            )

        if voucher_type == COMMISSION_ENTRY:
            return (
                scheme.partner_account
                or settings.default_partner_account
                or company.default_payable_account,
                scheme.commission_account
                or settings.default_commission_account
                or company.default_expense_account,
            )

    def get_party() -> Tuple[str, str]:
        if voucher_type == SUBSCRIPTION_ENTRY:
            return "Customer", share.customer

        if voucher_type == COMMISSION_ENTRY:
            return "Sales Partner", share.sales_partner

    def get_amounts() -> Tuple[float, float]:
        if voucher_type == SUBSCRIPTION_ENTRY:
            return scheme.unit_price, 0

        if voucher_type == COMMISSION_ENTRY:
            return 0, scheme.unit_price * share.commission_rate / 100.0

    def get_title():
        if voucher_type == SUBSCRIPTION_ENTRY:
            return share.customer_name

        if voucher_type == COMMISSION_ENTRY:
            return share.sales_partner_name

    def postprocess(source, target):
        target.update(
            {
                "voucher_type": voucher_type,
                "company": scheme.company,
                "title": get_title(),
            }
        )

        party_account, against_account = get_accounts()
        party_type, party = get_party()
        debit_amount, credit_amount = get_amounts()
        target.set(
            "accounts",
            [
                {
                    "account": party_account,
                    "debit_in_account_currency": debit_amount,
                    "credit_in_account_currency": credit_amount,
                    "party_type": party_type,
                    "party": party,
                    "marup_scheme": scheme.name,
                },
                {
                    "account": against_account,
                    "debit_in_account_currency": credit_amount,
                    "credit_in_account_currency": debit_amount,
                    "cost_center": scheme.cost_center or company.cost_center,
                    "marup_scheme": scheme.name,
                },
            ],
        )

    return get_mapped_doc(
        "Marup Subscription",
        subscription.name,
        {
            "Marup Subscription": {
                "doctype": "Journal Entry",
                "field_map": {
                    "posting_date": "posting_date",
                    "name": "marup_subscription",
                },
            }
        },
        None,
        postprocess,
    )
