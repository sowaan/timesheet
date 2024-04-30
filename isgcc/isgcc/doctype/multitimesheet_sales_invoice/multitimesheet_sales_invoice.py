# Copyright (c) 2024, Sowaan and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class MultiTimesheetSalesInvoice(Document):
	pass


@frappe.whitelist()
def get_timesheet_data(from_date, to_date, project=None, asset=None, customer=None, employee=None):
	total_billable_hours = 0
	total_billable_amount = 0
	filters=[
		["start_date", "Between", [from_date, to_date]],
		["docstatus", "=", 1],
		["Timesheet Detail","sales_invoice","is","not set"]
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
			"name", "employee", "start_date", "end_date", 
			"total_billable_hours", "total_billable_amount", 
			"total_billed_hours", "total_billed_amount", "custom_asset"
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
			total_billable_hours = total_billable_hours + (flt(timesheet.total_billable_hours) - flt(timesheet.total_billed_hours))
			total_billable_amount = total_billable_amount + (flt(timesheet.total_billable_amount) - flt(timesheet.total_billed_amount))
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
		"total_billable_hours": total_billable_hours, 
		"total_billable_amount": total_billable_amount,
	}

@frappe.whitelist()
def make_sales_invoice(source_name, item_code=None, customer=None, currency=None, timesheet_log=None):
	invoice = frappe.db.exists("Sales Invoice", {"custom_reference": source_name})
	if invoice:
		frappe.throw(_(f"Sales Invoice {invoice} is already created."))
	regular_hours_per_parent = {}
	overtime_hours_per_parent = {}
	timesheet_log = json.loads(timesheet_log)
	target = frappe.new_doc("Sales Invoice")
	timesheet = frappe.get_doc("MultiTimesheet Sales Invoice", source_name)
	target.custom_reference = source_name

	if not timesheet.total_billable_hours:
		frappe.throw(_("Invoice can't be made for zero billing hour"))

	hours = flt(timesheet.total_billable_hours)
	billing_amount = flt(timesheet.total_billable_amount)
	billing_rate = billing_amount / hours

	target.company = timesheet.company
	target.project = timesheet.project
	if customer:
		target.customer = customer

	if currency:
		target.currency = currency

	for tlog in timesheet_log:
		parent_name = tlog.get("custom_parent_name")
		asset_name = tlog.get("custom_asset")
		key = f"{parent_name}_Asset_{asset_name}"

		if key not in regular_hours_per_parent:
			regular_hours_per_parent[key] = {"hours": 0, "billing_rate": tlog.get("billing_rate", 0)}
		if key not in overtime_hours_per_parent:
			overtime_hours_per_parent[key] = {"hours": 0, "billing_rate": tlog.get("billing_rate", 0)}

		if tlog.get("custom_over_time") == 0:
			regular_hours_per_parent[key]["hours"] += tlog.get("hours")
		elif tlog.get("custom_over_time") == 1:
			overtime_hours_per_parent[key]["hours"] += tlog.get("hours")
	
	for parent_name, regular_hours in regular_hours_per_parent.items():
		split_asset = parent_name.split('_Asset_')

		if item_code and regular_hours.get("hours") > 0:
			target.append("items", {"item_code": item_code, "qty": regular_hours.get("hours"), "rate": regular_hours.get("billing_rate"), "asset": split_asset[1]})

	for parent_name, overtime_hours in overtime_hours_per_parent.items():
		split_asset = parent_name.split('_Asset_')
		if item_code and overtime_hours.get("hours") > 0:
			target.append("items", {"item_code": item_code, "qty": overtime_hours.get("hours"), "rate": overtime_hours.get("billing_rate"), "asset": split_asset[1], "custom_overtime": 1})

	for time_log in timesheet_log:
		if time_log.get("is_billable"):
			target.append(
				"timesheets",
				{
					"time_sheet": time_log.get("custom_parent_name"),
					"project_name": time_log.get("project_name"),
					"from_time": time_log.get("from_time"),
					"to_time": time_log.get("to_time"),
					"billing_hours": time_log.get("billing_hours"),
					"billing_amount": time_log.get("billing_amount"),
					"timesheet_detail": time_log.get("name"),
					"activity_type": time_log.get("activity_type"),
					"description": time_log.get("description"),
					"custom_overtime": time_log.get("custom_over_time")
				},
			)

	target.run_method("calculate_billing_amount_for_timesheet")
	target.run_method("set_missing_values")

	return target