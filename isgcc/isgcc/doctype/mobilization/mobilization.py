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
		["end_date", "Between", [start_date, end_date]]
	], fields=["employee", "asset"])
	print(mobilizations, "mobilizations \n\n\nn\n\n\n\n")
	employees = []
	assets = []

	for mobilization in mobilizations:
		if mobilization.employee not in employees:
			employees.append(mobilization.employee)
		if mobilization.asset not in assets:
			asset_status = frappe.db.get_value("Asset", mobilization.asset, "custom_mobilization_status")
			if asset_status == "Mobilized":
				assets.append(mobilization.asset)

	return {"employees": employees, "assets": assets}


@frappe.whitelist()
def demobilize_asset(name, asset):
	try:
		frappe.db.set_value('Asset', asset, 'custom_mobilization_status', 'Available')
		frappe.db.set_value('Mobilization', name, 'demobilized', 1)

		return "Asset Demobilized Successfully"
	except Exception as e:
		return e
