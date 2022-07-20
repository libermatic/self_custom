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

