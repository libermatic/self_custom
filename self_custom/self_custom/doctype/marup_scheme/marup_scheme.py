# Copyright (c) 2022, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.background_jobs import enqueue
from frappe.model.document import Document


class MarupScheme(Document):
    pass

