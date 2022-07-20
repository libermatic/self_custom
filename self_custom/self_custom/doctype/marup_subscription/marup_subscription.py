# Copyright (c) 2022, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

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

