# Copyright (c) 2022, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MarupPeriod(Document):
    def validate(self):
        try:
            marup_scheme, _ = self.marup_period_name.split("/")
            if marup_scheme != self.marup_scheme:
                raise Exception
        except Exception:
            frappe.throw("Invalid document naming")

    def before_insert(self):
        period_date = frappe.utils.datetime.datetime.strptime(
            self.marup_period_name.split("/")[1], "%y%m"
        )
        self.start_date = frappe.utils.get_first_day(period_date)
        self.end_date = frappe.utils.get_last_day(period_date)