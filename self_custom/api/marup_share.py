import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_marup_subscription(source_name, target_doc=None):
    def postprocess(source, target):
        pass

    return get_mapped_doc(
        "Marup Share",
        source_name,
        {
            "Marup Share": {
                "doctype": "Marup Subscription",
                "fieldmap": {"name": "marup_share", "marup_scheme": "marup_scheme"},
            }
        },
        target_doc,
        postprocess,
    )


def generate_subscriptions(posting_date=None):
    if not posting_date:
        posting_date = frappe.utils.today()

    periods = frappe.get_all(
        "Marup Period",
        filters={
            "disabled": 0,
            "start_date": ("<=", posting_date),
            "end_date": (">=", posting_date),
        },
        fields=["name", "marup_scheme"],
    )

    for period in periods:
        shares = frappe.get_all(
            "Marup Share",
            filters={"status": "Active", "marup_scheme": period.marup_scheme},
        )

        for share in shares:
            existing = frappe.db.exists(
                "Marup Subscription",
                {
                    "docstatus": 1,
                    "marup_share": share.name,
                    "marup_period": period.name,
                    "marup_scheme": period.marup_scheme,
                },
            )
            if not existing:
                subscription = make_marup_subscription(share.name)
                subscription.update(
                    {"marup_period": period.name, "posting_date": posting_date}
                )
                subscription.insert()
                subscription.submit()
