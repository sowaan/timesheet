# Copyright (c) 2024, Sowaan and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from frappe.model.document import Document
from erpnext import get_default_company
from frappe import _


class AutoTimesheetCreation(Document):
	def validate(self):
		activity_doc = frappe.get_doc("Activity Type", self.activity_type)
		activity_doc.billing_rate = self.billing_rate
		activity_doc.save()

	def on_submit(self):
		output = []
		for item in self.time_logs:
			custom_over_time_hours = item.get('custom_over_time_hours', 0)
			if custom_over_time_hours > 0:
				# Modify the initial item with adjusted 'hours'
				# item.hours -= custom_over_time_hours
				output.append(item)
				additional_item = {
					'activity_type': item.activity_type,
					'billing_amount': item.billing_amount,
					'completed': item.completed,
					'costing_amount': item.costing_amount,
					"custom_holiday": item.custom_holiday,
					'docstatus': item.docstatus,
					'doctype': item.doctype,
					'from_time': item.to_time,  # Use 'to_time' as 'from_time' for the additional item
					'to_time': (datetime.strptime(item.to_time, '%Y-%m-%d %H:%M:%S') 
								+ timedelta(hours=custom_over_time_hours)).strftime('%Y-%m-%d %H:%M:%S'),
					'hours': custom_over_time_hours,
					'custom_total_hrs': custom_over_time_hours,
					'is_billable': item.is_billable,
					'name': item.name,
					'owner': item.owner,
					'parent': item.parent,
					'parentfield': item.parentfield,
					'parenttype': item.parenttype,
					'custom_over_time': 1,
				}
				output.append(additional_item)
			else:
				output.append(item)
		timesheet_doc = frappe.get_doc({
			"doctype": "Timesheet",
			"customer": self.customer,
			"custom_asset": self.asset,
			"custom_auto_timesheet_creation": self.name,
			"parent_project": self.project,
			"custom_sales_order": self.sales_order,
			"custom_supplier": self.supplier,
			"custom_purchase_order": self.purchase_order,
		})
		if self.employee:
			timesheet_doc.employee = self.employee
	
		for timsh in output:
			timesheet_doc.append("time_logs", {
				"activity_type": timsh.get("activity_type"),
				"from_time": timsh.get("from_time"),
				"to_time": timsh.get("to_time"),
				"custom_total_hrs": timsh.get("custom_total_hrs"),
				"hours": timsh.get("hours"),
				"description": timsh.get("description"),
				"expected_hours": timsh.get("expected_hours"),
				"completed": timsh.get("completed"),
				"project": self.project,
				"task": timsh.get("task"),
				"custom_holiday": timsh.get("custom_holiday"),
				"custom_regular_hours": timsh.get("custom_regular_hours"),
				"custom_over_time_hours": timsh.get("custom_over_time_hours"),
				"is_billable": timsh.get("is_billable"),
				"base_billing_rate": timsh.get("base_billing_rate"),
				"base_billing_amount": timsh.get("base_billing_amount"),
				"costing_rate": self.costing_rate,
				"costing_amount": self.costing_rate * timsh.get("custom_total_hrs"),
				"custom_over_time": timsh.get("custom_over_time"),
			})	
		timesheet_doc.validate()
		timesheet_doc.insert()
		timesheet_doc.submit()


@frappe.whitelist()
def make_auto_timesheet_creation(mobiliza, employee, customer, asset, sales_order):
	doc = frappe.new_doc("Auto Timesheet Creation")
	doc.mobilization = mobiliza
	doc.employee = employee
	doc.customer = customer,
	doc.asset = asset
	doc.sales_order = sales_order

	return doc


@frappe.whitelist()
def get_holiday_list():
	company = get_default_company() or frappe.get_all("Company")[0].name

	holiday = frappe.get_cached_value("Company", company, "default_holiday_list")
	if not holiday:
		frappe.throw(
			_("Please set a default Holiday List for Company {0}").format(
				frappe.bold(get_default_company())
			)
		)
	holiday_list = frappe.get_doc("Holiday List", holiday)
	# print(holiday_list.holidays, "Checimg \n\n\n\n")
	return holiday_list.holidays
