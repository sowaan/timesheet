# Copyright (c) 2024, Sowaan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Mobilization(Document):
	def on_submit(self):
		asset_doc = frappe.get_doc("Asset", self.asset)
		asset_doc.custom_mobilization_status = "Mobilized"
		asset_doc.submit()


	def on_cancel(self):
		asset_doc = frappe.get_doc("Asset", self.asset)
		asset_doc.custom_mobilization_status = "Available"
		asset_doc.submit()

@frappe.whitelist()
def get_mobilization_list(start_date, end_date):
	mobilizations = frappe.get_all("Mobilization", filters=[
		["docstatus", "=", 1],
		["start_date", "Between", [start_date, end_date]]
	], fields=["employee", "asset"])
	employees = []
	assets = []

	for mobilization in mobilizations:
		if mobilization.employee not in employees:
			employees.append(mobilization.employee)
		if mobilization.asset not in assets:
			assets.append(mobilization.asset)
	return {"employees": employees, "assets": assets}