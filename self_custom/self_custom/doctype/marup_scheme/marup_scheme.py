# Copyright (c) 2022, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.background_jobs import enqueue
from frappe.model.document import Document


class MarupScheme(Document):
    pass

    def on_update(self):
        self._enqueue_create_periods()

    def on_trash(self):
        for (name,) in frappe.get_all(
            "Marup Period",
            filters={"marup_scheme": self.name},
            order_by="name asc",
            as_list=1,
        ):
            frappe.delete_doc("Marup Period", name)

    @frappe.whitelist()
    def disable_period(self, period):
        if frappe.db.exists(
            {
                "doctype": "Marup Subscription",
                "docstatus": 1,
                "marup_period": self.name,
            }
        ):
            frappe.throw(
                "Cannot disable: <strong>Marup Subscription</strong> already exists "
                "for this period"
            )

        frappe.db.set_value("Marup Period", period, "disabled", 1)
        self._enqueue_create_periods()

    def _enqueue_create_periods(self):
        enqueue(
            _create_periods,
            queue="default",
            timeout=10000,
            event="create_marup_periods",
            job_name=f"{self.name}:create_marup_periods",
            doc=self,
            ignore_links=self.flags.in_insert,
        )


def _create_periods(doc, ignore_links):
    def get_args(index) -> str:
        start_date = frappe.utils.get_first_day(
            frappe.utils.add_months(doc.start_date, index)
        )
        return f'{doc.name}/{start_date.strftime("%y%m")}'

    existing_periods = frappe.get_all(
        "Marup Period",
        filters={"marup_scheme": doc.name},
        fields=["name", "disabled"],
        order_by="name asc",
    )
    disabled_periods = [x for x in existing_periods if x.get("disabled") == 1]

    names = [get_args(x + 1) for x in range(doc.duration + len(disabled_periods))]

    if len(existing_periods) > len(names):
        for period in existing_periods[len(names) :]:
            frappe.delete_doc("Marup Period", period.get("name"))
        return

    existing_names = [x.get("name") for x in existing_periods]
    for name in names:
        if name not in existing_names:
            frappe.get_doc(
                {
                    "doctype": "Marup Period",
                    "marup_period_name": name,
                    "marup_scheme": doc.name,
                }
            ).insert(ignore_links=ignore_links)
