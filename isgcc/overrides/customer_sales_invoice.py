import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.setup.utils import get_exchange_rate

class CustomerSalesInvoice(Document):
    pass

@frappe.whitelist()
def make_sales_invoice(source_name, item_code=None, customer=None, currency=None, timesheet_log=None):
    timesheet_log = json.loads(timesheet_log)
    target = frappe.new_doc("Sales Invoice")
    timesheet = frappe.get_doc("Timesheet", source_name)

    if not timesheet.total_billable_hours:
        frappe.throw(_("Invoice can't be made for zero billing hour"))

    if timesheet.total_billable_hours == timesheet.total_billed_hours:
        frappe.throw(_("Invoice already created for all billing hours"))

    hours = flt(timesheet.total_billable_hours) - flt(timesheet.total_billed_hours)
    billing_amount = flt(timesheet.total_billable_amount) - flt(timesheet.total_billed_amount)
    billing_rate = billing_amount / hours

    target.company = timesheet.company
    target.project = timesheet.parent_project
    if customer:
        target.customer = customer

    if currency:
        target.currency = currency
    reguler_hours = 0
    overtime_hours = 0
    for tlog in timesheet_log:
        if tlog.get("custom_over_time") == 0:
            reguler_hours = reguler_hours + tlog.get("hours")
        if tlog.get("custom_over_time") == 1:
            overtime_hours = overtime_hours + tlog.get("hours")

    if item_code:
        if reguler_hours > 0:
            target.append("items", {"item_code": item_code, "qty": reguler_hours, "rate": billing_rate, "asset": timesheet.custom_asset, "sales_order": timesheet.custom_sales_order})
        if overtime_hours > 0:
            target.append("items", {"item_code": item_code, "qty": overtime_hours, "rate": billing_rate, "asset": timesheet.custom_asset, "sales_order": timesheet.custom_sales_order, "custom_overtime": 1})

    for time_log in timesheet_log:
        if time_log.get("is_billable"):
            target.append(
                "timesheets",
                {
                    "time_sheet": timesheet.name,
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


@frappe.whitelist()
def get_timesheet_detail_rate(timelog, currency):
	timelog_detail = frappe.db.sql(
		"""SELECT tsd.billing_amount as billing_amount,
		ts.currency as currency FROM `tabTimesheet Detail` tsd
		INNER JOIN `tabTimesheet` ts ON ts.name=COALESCE(tsd.custom_parent_name, tsd.parent)
		WHERE tsd.name = '{0}'""".format(
			timelog
		),
		as_dict=1,
	)[0]

	if timelog_detail.currency:
		exchange_rate = get_exchange_rate(timelog_detail.currency, currency)
        
		return timelog_detail.billing_amount * exchange_rate
    
	return timelog_detail.billing_amount