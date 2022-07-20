import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from self_custom.doc_events.journal_entry import MARUP_VOUCHER_TYPES


def execute():
    _create_custom_fields()
    _update_voucher_type_options()


def _create_custom_fields():
    depends_on = f"eval:{str(MARUP_VOUCHER_TYPES)}.includes(doc.voucher_type)"
    create_custom_field(
        "Journal Entry",
        {
            "fieldname": "marup_subscription",
            "label": "Marup Subscription",
            "fieldtype": "Link",
            "options": "Marup Subscription",
            "insert_after": "reference",
            "depends_on": depends_on,
            "mandatory_depends_on": depends_on,
        },
    )


def _update_voucher_type_options():
    entry_types = current_options = (
        frappe.get_meta("Journal Entry").get_field("voucher_type").options
    )

    for entry_type in MARUP_VOUCHER_TYPES:
        if entry_type not in entry_types:
            entry_types += f"\n{entry_type}"

    if entry_types != current_options:
        if frappe.db.exists("Property Setter", "Journal Entry-voucher_type-options"):
            property_setter = frappe.get_doc(
                "Property Setter", "Journal Entry-voucher_type-options"
            )
            property_setter.value = entry_types
            property_setter.save()
        else:
            frappe.get_doc(
                {
                    "doctype": "Property Setter",
                    "doctype_or_field": "DocField",
                    "doc_type": "Journal Entry",
                    "field_name": "voucher_type",
                    "property": "options",
                    "property_type": "Text",
                    "value": entry_types,
                }
            ).insert()
