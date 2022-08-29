import frappe

def execute():
    frappe.get_doc({
        "doctype": "Accounting Dimension",
        "document_type": "Marup Scheme",
        "label": "Marup Scheme",
    }).insert(ignore_if_duplicate=True)