// Copyright (c) 2024, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on("MultiTimesheet Sales Invoice", {
  async refresh(frm) {
    frm.dashboard.links_area.body.find(".btn-new").each(function (i, el) {
      $(el).hide();
    });
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button(__("Make Sales Invoice"), function () {
        frm.trigger("make_invoices");
      });
    }
  },

  make_invoices(frm) {
    frappe.call({
      type: "GET",
      method:
        "isgcc.isgcc.doctype.multitimesheet_sales_invoice.multitimesheet_sales_invoice.make_sales_invoice",
      args: {
        source_name: frm.doc.name,
        item_code: frm.doc.item,
        customer: frm.doc.customer,
        currency: frm.doc.currency,
        timesheet_log: frm.doc.timesheets,
      },
      freeze: true,
      callback: function (r) {
        if (!r.exc) {
          frappe.model.sync(r.message);
          frappe.set_route("Form", r.message.doctype, r.message.name);
        }
      },
    });
  },

  async fetch_timesheets(frm) {
    const kwargs = {
      from_date: frm.doc.from_date,
      to_date: frm.doc.to_date,
      project: frm.doc.project,
      asset: frm.doc.asset,
      customer: frm.doc.customer,
      employee: frm.doc.employee,
    };
    const data = await frm.events.get_timesheet_data(frm, kwargs);
    if (data.timesheets.length === 0) {
      frappe.msgprint(__("No timesheets found between selected dates."));
    }
    frm.set_value("total_billable_hours", data.total_billable_hours);
    frm.set_value("total_billable_amount", data.total_billable_amount);
    await frm.events.set_timesheet_data(frm, data.timesheets);
  },

  async get_timesheet_data(frm, kwargs) {
    return frappe
      .call({
        method:
          "isgcc.isgcc.doctype.multitimesheet_sales_invoice.multitimesheet_sales_invoice.get_timesheet_data",
        args: kwargs,
      })
      .then((r) => {
        if (!r.exc) {
          return r.message;
        } else {
          return [];
        }
      });
  },

  set_timesheet_data: function (frm, timesheets) {
    frm.set_value("timesheets", []);
    var index = 0;
    timesheets.forEach(async (timesheet) => {
      timesheet.details.forEach(async (log, i) => {
        index = index + 1;
        frm.events.append_time_log(frm, log, timesheet.custom_asset, index);
      });
    });
    frm.refresh_field("timesheets");
  },

  append_time_log: function (frm, time_log, asset, index) {
    const row = frm.add_child("timesheets");
    row.activity_type = time_log.activity_type;
    time_log.idx = index;
    row.custom_asset = asset;
    row.base_billing_amount = time_log.billing_amount;
    row.base_billing_rate = time_log.billing_rate;
    row.base_costing_amount = time_log.costing_amount;
    row.base_costing_rate = time_log.costing_rate;
    row.billing_amount = time_log.billing_amount;
    row.billing_hours = time_log.billing_hours;
    row.billing_rate = time_log.billing_rate;
    row.completed = time_log.completed;
    row.costing_amount = time_log.costing_amount;
    row.costing_rate = time_log.costing_rate;
    row.creation = time_log.creation;
    row.custom_holiday = time_log.custom_holiday;
    row.custom_over_time = time_log.custom_over_time;
    row.custom_over_time_hours = time_log.custom_over_time_hours;
    row.custom_reason = time_log.custom_reason;
    row.custom_regular_hours = time_log.custom_regular_hours;
    row.description = time_log.description;
    row.docstatus = time_log.docstatus;
    row.expected_hours = time_log.expected_hours;
    row.from_time = time_log.from_time;
    row.hours = time_log.hours;
    row.is_billable = time_log.is_billable;
    row.modified = time_log.modified;
    row.modified_by = time_log.modified_by;
    row.name = time_log.name;
    row.owner = time_log.owner;
    row.parent = time_log.parent;
    row.custom_parent_name = time_log.parent;
    row.parentfield = time_log.parentfield;
    row.parenttype = time_log.parenttype;
    row.project = time_log.project;
    row.project_name = time_log.project_name;
    row.sales_invoice = time_log.sales_invoice;
    row.task = time_log.task;
    row.to_time = time_log.to_time;
  },
});
