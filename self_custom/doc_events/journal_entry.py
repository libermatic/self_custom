import frappe


SUBSCRIPTION_ENTRY = "Subscription Entry"
COMMISSION_ENTRY = "Commission Entry"
MARUP_VOUCHER_TYPES = [SUBSCRIPTION_ENTRY, COMMISSION_ENTRY]


def validate(doc, method):
    if doc.voucher_type in MARUP_VOUCHER_TYPES:
        if not doc.marup_subscription:
            frappe.throw(
                "<em>Marup Subscription</em> is required when <em>Entry Type</em> is "
                f"<em>{doc.voucher_type}</em>."
            )

        existing_je = frappe.db.exists(
            "Journal Entry",
            {
                "docstatus": 1,
                "voucher_type": doc.voucher_type,
                "marup_subscription": doc.marup_subscription,
            },
        )
        if existing_je:
            frappe.throw(
                f'{frappe.get_desk_link("Journal Entry", existing_je)} already exists '
                f"as a <em>{doc.voucher_type}</em>."
            )


def before_submit(doc, method):
    if doc.voucher_type not in MARUP_VOUCHER_TYPES:
        doc.marup_subscription = None


def on_submit(doc, method):
    if doc.marup_subscription:
        msdoc = frappe.get_doc("Marup Subscription", doc.marup_subscription)
        if doc.voucher_type == SUBSCRIPTION_ENTRY:
            msdoc.set_subscription_status("Billed")
        elif doc.voucher_type == COMMISSION_ENTRY:
            msdoc.set_commission_status("Billed")


def before_cancel(doc, method):
    existing_pes = frappe.get_all(
        "Payment Entry Reference",
        filters={
            "reference_doctype": "Journal Entry",
            "reference_name": doc.name,
            "docstatus": 1,
        },
        fields=["parent"],
    )
    if existing_pes:
        pe_links = [
            frappe.get_desk_link("Payment Entry", x.get("parent")) for x in existing_pes
        ]
        frappe.throw(
            f'{", ".join(pe_links)} exists for this <strong>Journal Entry</strong>. '
            "Please cancel that first."
        )


def on_cancel(doc, method):
    if doc.marup_subscription:
        msdoc = frappe.get_doc("Marup Subscription", doc.marup_subscription)
        if doc.voucher_type == SUBSCRIPTION_ENTRY:
            msdoc.set_subscription_status(None)
        elif doc.voucher_type == COMMISSION_ENTRY:
            msdoc.set_commission_status(None)

