# Copyright (c) 2022, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MarupShare(Document):
    def before_insert(self):
        self.status = "Active"

    @frappe.whitelist()
    def set_settled(self):
        self.status = "Settled"
        self.save()
