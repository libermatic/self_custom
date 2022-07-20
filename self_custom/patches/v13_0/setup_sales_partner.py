import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def execute():
    _create_custom_fields()
    _update_meta()
    _update_fields()
    _create_party_type()


def _create_custom_fields():
    create_custom_field(
        "Sales Partner",
        {
            "fieldname": "partner_id",
            "label": "Partner ID",
            "fieldtype": "Data",
            "insert_after": "",
            "reqd": 1,
        },
    )


def _update_meta():
    def set_property_setter(property, value):
        name = f"Sales Partner-main-{property}"
        if frappe.db.exists("Property Setter", name):
            property_setter = frappe.get_doc("Property Setter", name)
            property_setter.value = value
            property_setter.save()
        else:
            frappe.get_doc(
                {
                    "doctype": "Property Setter",
                    "doctype_or_field": "DocType",
                    "doc_type": "Sales Partner",
                    "property": property,
                    "property_type": "Data",
                    "value": value,
                }
            ).insert()

    set_property_setter("autoname", "field:partner_id")
    set_property_setter("search_fields", "partner_name")


def _update_fields():
    if frappe.db.exists("Property Setter", "Sales Partner-partner_name-unique"):
        property_setter = frappe.get_doc(
            "Property Setter", "Sales Partner-partner_name-unique"
        )
        property_setter.value = 0
        property_setter.save()
    else:
        frappe.get_doc(
            {
                "doctype": "Property Setter",
                "doctype_or_field": "DocField",
                "doc_type": "Sales Partner",
                "field_name": "partner_name",
                "property": "unique",
                "property_type": "Check",
                "value": 0,
            }
        ).insert()


def _create_party_type():
    frappe.get_doc(
        {
            "doctype": "Party Type",
            "party_type": "Sales Partner",
            "account_type": "Payable",
        }
    ).insert(ignore_if_duplicate=True)
