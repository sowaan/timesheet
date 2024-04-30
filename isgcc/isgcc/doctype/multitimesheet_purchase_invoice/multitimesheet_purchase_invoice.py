# Copyright (c) 2024, Sowaan and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class MultiTimesheetPurchaseInvoice(Document):
	def on_submit(self):
		regular_hours_per_parent = {}
		overtime_hours_per_parent = {}
		timesheet_log = self.timesheets
		target = frappe.new_doc("Purchase Invoice")
		target.custom_reference = self.name

		if not self.total_billable_hours:
			frappe.throw(_("Invoice can't be made for zero billing hour"))

		hours = flt(self.total_billable_hours)
		billing_amount = flt(self.total_billable_amount)
		billing_rate = billing_amount / hours

		target.company = self.company
		target.project = self.project
		target.supplier = self.supplier

		for tlog in timesheet_log:
			parent_name = tlog.get("custom_parent_name")
			asset_name = tlog.get("custom_asset")
			key = f"{parent_name}_Asset_{asset_name}"

			if key not in regular_hours_per_parent:
				regular_hours_per_parent[key] = {"hours": 0, "costing_rate": tlog.get("costing_rate", 0)}
			if key not in overtime_hours_per_parent:
				overtime_hours_per_parent[key] = {"hours": 0, "costing_rate": tlog.get("costing_rate", 0)}

			if tlog.get("custom_over_time") == 0:
				regular_hours_per_parent[key]["hours"] += tlog.get("hours")
			elif tlog.get("custom_over_time") == 1:
				overtime_hours_per_parent[key]["hours"] += tlog.get("hours")
		
		for parent_name, regular_hours in regular_hours_per_parent.items():
			split_asset = parent_name.split('_Asset_')

			if self.item and regular_hours.get("hours") > 0:
				target.append("items", {"item_code": self.item, "qty": regular_hours.get("hours"), "rate": regular_hours.get("costing_rate"), "asset": split_asset[1]})

		for parent_name, overtime_hours in overtime_hours_per_parent.items():
			split_asset = parent_name.split('_Asset_')
			if self.item and overtime_hours.get("hours") > 0:
				target.append("items", {"item_code": self.item, "qty": overtime_hours.get("hours"), "rate": overtime_hours.get("costing_rate"), "asset": split_asset[1], "custom_overtime": 1})

		target.run_method("calculate_billing_amount_for_timesheet")
		target.run_method("set_missing_values")
		target.insert()

		for tlog in timesheet_log:
			doc = frappe.get_doc("Timesheet", tlog.custom_parent_name)
			for log in doc.time_logs:
				frappe.db.set_value("Timesheet Detail", log.name, "custom_purchase_invoice", target.name)


	def on_cancel(self):
		self.unlink_pr_in_timesheet()

	def unlink_pr_in_timesheet(self):
		timesheet_log = self.timesheets
		for tlog in timesheet_log:
			doc = frappe.get_doc("Timesheet", tlog.custom_parent_name)
			for log in doc.time_logs:
				frappe.db.set_value("Timesheet Detail", log.name, "custom_purchase_invoice", None)



@frappe.whitelist()
def get_timesheet_data(from_date, to_date, supplier=None, project=None, asset=None, customer=None, employee=None):
	filters=[
		["start_date", "Between", [from_date, to_date]],
		["docstatus", "=", 1],
		["Timesheet Detail","custom_purchase_invoice","is","not set"],
		["custom_asset_type", "=", "Hired"],
		["custom_supplier", "=", supplier],
	]

	if project:
		filters.append(["parent_project", "=", project])

	if asset:
		filters.append(["custom_asset", "=", asset])

	if customer:
		filters.append(["customer", "=", customer])

	if employee:
		filters.append(["employee", "=", employee])
	
	timesheets = frappe.get_all(
		"Timesheet",
		fields=[
			"name", "employee", "start_date", "end_date", "custom_asset"
		],
		filters=filters,
		as_list=False,
    )
	timesheet_ids = set()
	unique_timesheets = []
	for timesheet in timesheets:
		timesheet_id = timesheet["name"]
		if timesheet_id not in timesheet_ids:
			timesheet_details = frappe.get_all(
				"Timesheet Detail",
				fields=["*"],
				filters={"parent": timesheet_id},
				as_list=False
			)
			timesheet["details"] = timesheet_details
			unique_timesheets.append(timesheet)
			timesheet_ids.add(timesheet_id)
	for timesheet in unique_timesheets:
		timesheet_details = frappe.get_all(
			"Timesheet Detail",
			fields=["*"],
			filters={"parent": timesheet["name"]},
			as_list=False,
			order_by="from_time"
		)
		timesheet["details"] = timesheet_details

	return {
		"timesheets": unique_timesheets,
	}