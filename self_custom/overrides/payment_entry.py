import json
from six import string_types
import frappe

from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_party_account,
    get_account_currency,
    get_balance_on,
    get_account_details,
    get_party_account_based_on_invoice_discounting,
)


@frappe.whitelist()
def get_party_details(company, party_type, party, date, cost_center=None):
    from erpnext.accounts.doctype.payment_entry.payment_entry import (
        get_party_details as _get_party_details,
    )

    if party_type != "Sales Partner":
        return _get_party_details(company, party_type, party, date, cost_center)

    party_account = frappe.get_value(
        "SELF Default Account",
        filters={"company": company},
        fieldname="default_partner_account",
    ) or get_party_account(party_type, party, company)
    account_currency = get_account_currency(party_account)
    account_balance = get_balance_on(party_account, date, cost_center=cost_center)
    party_name = frappe.db.get_value(party_type, party, "partner_name")
    party_balance = get_balance_on(
        party_type=party_type, party=party, cost_center=cost_center
    )
    return {
        "party_account": party_account,
        "party_name": party_name,
        "party_account_currency": account_currency,
        "party_balance": party_balance,
        "account_balance": account_balance,
        "bank_account": None,
    }


@frappe.whitelist()
def get_outstanding_reference_documents(args):
    from erpnext.accounts.doctype.payment_entry.payment_entry import (
        get_outstanding_reference_documents as _get_outstanding_reference_documents,
        get_outstanding_invoices,
        get_exchange_rate,
    )

    if isinstance(args, string_types):
        args = json.loads(args)

    if args.get("party_type") != "Sales Partner":
        return _get_outstanding_reference_documents(args)

    party_account_currency = get_account_currency(args.get("party_account"))
    company_currency = frappe.get_cached_value(
        "Company", args.get("company"), "default_currency"
    )

    # Get positive outstanding sales /purchase invoices/ Fees
    condition = ""
    if args.get("voucher_type") and args.get("voucher_no"):
        condition = " and voucher_type={0} and voucher_no={1}".format(
            frappe.db.escape(args["voucher_type"]), frappe.db.escape(args["voucher_no"])
        )

    # Add cost center condition
    if args.get("cost_center"):
        condition += " and cost_center='%s'" % args.get("cost_center")

    date_fields_dict = {
        "posting_date": ["from_posting_date", "to_posting_date"],
        "due_date": ["from_due_date", "to_due_date"],
    }

    for fieldname, date_fields in date_fields_dict.items():
        if args.get(date_fields[0]) and args.get(date_fields[1]):
            condition += " and {0} between '{1}' and '{2}'".format(
                fieldname, args.get(date_fields[0]), args.get(date_fields[1])
            )

    if args.get("company"):
        condition += " and company = {0}".format(frappe.db.escape(args.get("company")))

    outstanding_invoices = get_outstanding_invoices(
        args.get("party_type"),
        args.get("party"),
        args.get("party_account"),
        filters=args,
        condition=condition,
    )

    for d in outstanding_invoices:
        d["exchange_rate"] = 1
        if party_account_currency != company_currency:
            if d.voucher_type == "Journal Entry":
                d["exchange_rate"] = get_exchange_rate(
                    party_account_currency, company_currency, d.posting_date
                )

    if not outstanding_invoices:
        frappe.msgprint(
            frappe._(
                "No outstanding invoices found for the {0} {1} which qualify the "
                "filters you have specified."
            ).format(
                frappe._(args.get("party_type")).lower(), frappe.bold(args.get("party"))
            )
        )

    return outstanding_invoices


def set_missing_values(self):
    if self.payment_type == "Internal Transfer":
        for field in (
            "party",
            "party_balance",
            "total_allocated_amount",
            "base_total_allocated_amount",
            "unallocated_amount",
        ):
            self.set(field, None)
        self.references = []
    else:
        if not self.party_type:
            frappe.throw(frappe._("Party Type is mandatory"))

        if not self.party:
            frappe.throw(frappe._("Party is mandatory"))

        _party_name = (
            "partner_name"
            if self.party_type == "Sales Partner"
            else "title"
            if self.party_type in ("Student", "Shareholder")
            else self.party_type.lower() + "_name"
        )
        self.party_name = frappe.db.get_value(self.party_type, self.party, _party_name)

    if self.party:
        if not self.party_balance:
            self.party_balance = get_balance_on(
                party_type=self.party_type,
                party=self.party,
                date=self.posting_date,
                company=self.company,
            )

        if not self.party_account:
            party_account = get_party_account(self.party_type, self.party, self.company)
            self.set(self.party_account_field, party_account)
            self.party_account = party_account

    if self.paid_from and not (
        self.paid_from_account_currency or self.paid_from_account_balance
    ):
        acc = get_account_details(self.paid_from, self.posting_date, self.cost_center)
        self.paid_from_account_currency = acc.account_currency
        self.paid_from_account_balance = acc.account_balance

    if self.paid_to and not (
        self.paid_to_account_currency or self.paid_to_account_balance
    ):
        acc = get_account_details(self.paid_to, self.posting_date, self.cost_center)
        self.paid_to_account_currency = acc.account_currency
        self.paid_to_account_balance = acc.account_balance

    self.party_account_currency = (
        self.paid_from_account_currency
        if self.payment_type == "Receive"
        else self.paid_to_account_currency
    )

    self.set_missing_ref_details()


def validate_reference_documents(self):
    if self.party_type == "Student":
        valid_reference_doctypes = "Fees"
    elif self.party_type == "Customer":
        valid_reference_doctypes = (
            "Sales Order",
            "Sales Invoice",
            "Journal Entry",
            "Dunning",
        )
    elif self.party_type == "Supplier":
        valid_reference_doctypes = (
            "Purchase Order",
            "Purchase Invoice",
            "Journal Entry",
        )
    elif self.party_type == "Employee":
        valid_reference_doctypes = (
            "Expense Claim",
            "Journal Entry",
            "Employee Advance",
            "Gratuity",
        )
    elif self.party_type == "Shareholder":
        valid_reference_doctypes = "Journal Entry"
    elif self.party_type == "Donor":
        valid_reference_doctypes = "Donation"
    elif self.party_type == "Sales Partner":
        valid_reference_doctypes = "Journal Entry"

    for d in self.get("references"):
        if not d.allocated_amount:
            continue
        if d.reference_doctype not in valid_reference_doctypes:
            frappe.throw(
                frappe._("Reference Doctype must be one of {0}").format(
                    frappe.utils.comma_or(valid_reference_doctypes)
                )
            )

        elif d.reference_name:
            if not frappe.db.exists(d.reference_doctype, d.reference_name):
                frappe.throw(
                    frappe._("{0} {1} does not exist").format(
                        d.reference_doctype, d.reference_name
                    )
                )
            else:
                ref_doc = frappe.get_doc(d.reference_doctype, d.reference_name)

                if d.reference_doctype != "Journal Entry":
                    if self.party != ref_doc.get(frappe.scrub(self.party_type)):
                        frappe.throw(
                            frappe._("{0} {1} is not associated with {2} {3}").format(
                                d.reference_doctype,
                                d.reference_name,
                                self.party_type,
                                self.party,
                            )
                        )
                else:
                    self.validate_journal_entry()

                if d.reference_doctype in (
                    "Sales Invoice",
                    "Purchase Invoice",
                    "Expense Claim",
                    "Fees",
                ):
                    if self.party_type == "Customer":
                        ref_party_account = (
                            get_party_account_based_on_invoice_discounting(
                                d.reference_name
                            )
                            or ref_doc.debit_to
                        )
                    elif self.party_type == "Student":
                        ref_party_account = ref_doc.receivable_account
                    elif self.party_type == "Supplier":
                        ref_party_account = ref_doc.credit_to
                    elif self.party_type == "Employee":
                        ref_party_account = ref_doc.payable_account

                    if ref_party_account != self.party_account:
                        frappe.throw(
                            frappe._(
                                "{0} {1} is associated with {2}, but Party Account is {3}"
                            ).format(
                                d.reference_doctype,
                                d.reference_name,
                                ref_party_account,
                                self.party_account,
                            )
                        )

                    if ref_doc.doctype == "Purchase Invoice" and ref_doc.get("on_hold"):
                        frappe.throw(
                            frappe._("{0} {1} is on hold").format(
                                d.reference_doctype, d.reference_name
                            ),
                            title=frappe._("Invalid Invoice"),
                        )

                if ref_doc.docstatus != 1:
                    frappe.throw(
                        frappe._("{0} {1} must be submitted").format(
                            d.reference_doctype, d.reference_name
                        )
                    )

