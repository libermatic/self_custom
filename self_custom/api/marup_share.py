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
