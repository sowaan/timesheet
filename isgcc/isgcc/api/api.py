import frappe
from frappe import _
from frappe.utils import flt


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

