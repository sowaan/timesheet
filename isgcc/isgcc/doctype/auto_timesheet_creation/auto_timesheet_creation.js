// Copyright (c) 2024, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Auto Timesheet Creation", {
  refresh(frm) {
    frm.set_query("sales_order", function () {
      return {
        filters: [
          ["customer", "=", frm.doc.customer],
          ["Sales Order Item", "asset", "=", frm.doc.asset],
        ],
      };
    });
    frm.set_query("purchase_order", function () {
      return {
        filters: [
          ["Purchase Order Item", "asset", "=", frm.doc.asset],
          ["Purchase Order", "docstatus", "=", 1],
        ],
      };
    });
    frm.trigger("set_volumn_rate");
  },

  sales_order(frm) {
    frm.trigger("set_volumn_rate");
  },

  purchase_order(frm) {
    frm.trigger("set_volumn_rate");
  },

  asset(frm) {
    frm.trigger("set_volumn_rate");
  },

  set_volumn_rate(frm) {
    if (frm.doc.sales_order && frm.doc.asset) {
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Sales Order",
          name: frm.doc.sales_order,
        },
        callback: function (r) {
          if (r.message.items) {
            for (let i = 0; i < r.message.items.length; i++) {
              const ele = r.message.items[i];
              if (ele.asset === frm.doc.asset) {
                frm.set_value("so_volume", ele.amount);
                if (!frm.doc.billable_hrs) {
                  frm.set_value("billable_hrs", ele.qty);
                }
                if (!frm.doc.overtime_billable_hrs) {
                  frm.set_value("overtime_billable_hrs", ele.qty);
                }
              }
            }
          }
        },
      });
    }
    if (frm.doc.purchase_order && frm.doc.asset) {
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Purchase Order",
          name: frm.doc.purchase_order,
        },
        callback(r) {
          var p_order = r.message;
          if (p_order) {
            if (p_order.items) {
              for (let i = 0; i < p_order.items.length; i++) {
                const ele = p_order.items[i];
                if (ele.asset === frm.doc.asset) {
                  frm.set_value("po_volume", ele.amount);
                  if (!frm.doc.costing_hrs) {
                    frm.set_value("costing_hrs", ele.qty);
                  }
                }
              }
            }
          }
        },
      });
    }
  },

  async show_timesheets(frm) {
    frm.set_value("time_logs", "");
    let holiday_list = [];
    const totalDays =
      frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1;

    await frappe.call({
      method:
        "isgcc.isgcc.doctype.auto_timesheet_creation.auto_timesheet_creation.get_holiday_list",
      callback: function (r) {
        if (r.message) {
          holiday_list = r.message;
        }
      },
    });

    if (!frm.doc.activity_type) {
      frappe.throw(__("Please Select Activity Type"));
      return;
    }

    for (let i = 0; i < totalDays; i++) {
      var row = frappe.model.add_child(
        frm.doc,
        "Timesheet Detail",
        "time_logs"
      );
      var date = frappe.datetime.add_days(frm.doc.from_date, i);
      let exists = holiday_list.some(
        (item) => item.holiday_date.toString() == date.toString()
      );

      row.activity_type = frm.doc.activity_type;
      row.from_time = date;
      row.custom_regular_hours = exists ? 0 : frm.doc.regular_hrs;
      row.hours = exists ? 0.0004 : row.custom_regular_hours;
      row.custom_holiday = exists ? 1 : 0;
      row.custom_total_hrs = row.hours;

      if (row.hours) {
        let d = moment(row.from_time).add(row.hours, "hours");
        row.to_time = d.format(frappe.defaultDatetimeFormat);
      }
    }

    frm.refresh_field("time_logs");
    let total_hours = 0;
    let total_regular_hours = 0;
    let total_overtime_hours = 0;
    for (let i = 0; i < frm.doc.time_logs.length; i++) {
      const ele = frm.doc.time_logs[i];
      total_hours += ele.custom_total_hrs;
      total_regular_hours += ele.custom_regular_hours;
      total_overtime_hours += ele.custom_over_time_hours;
    }
    frm.set_value("total_hours", total_hours);
    frm.set_value("total_regular_hours", total_regular_hours);
    frm.set_value("total_overtime_hours", total_overtime_hours);
  },

  activity_type(frm) {
    if (frm.doc.time_logs != null) {
      frm.trigger("show_timesheets");
    }
  },

  to_date(frm) {
    if (frm.doc.to_date < frm.doc.from_date) {
      frm.set_value("to_date", frm.doc.from_date);
      frappe.throw(__("To Date must be greater than From Date"));
    }
  },

  billable_hrs(frm) {
    if (frm.doc.billable_hrs) {
      frm.set_value("billing_rate", frm.doc.so_volume / frm.doc.billable_hrs);
    }
  },
  costing_hrs(frm) {
    if (frm.doc.costing_hrs) {
      frm.set_value("costing_rate", frm.doc.po_volume / frm.doc.costing_hrs);
    }
  },
});

frappe.ui.form.on("Timesheet Detail", {
  time_logs_remove: function (frm, cdt, cdn) {
    calculate_time_and_amount(frm, cdt, cdn);
  },

  task: (frm, cdt, cdn) => {
    let row = frm.selected_doc;
    if (row.task) {
      frappe.db.get_value("Task", row.task, "project", (r) => {
        frappe.model.set_value(cdt, cdn, "project", r.project);
      });
    }
  },

  from_time: function (frm, cdt, cdn) {
    calculate_end_time(frm, cdt, cdn);
  },

  to_time: function (frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    if (frm._setting_hours) return;

    var hours =
      moment(child.to_time).diff(moment(child.from_time), "seconds") / 3600;
    frappe.model.set_value(cdt, cdn, "hours", hours);
    calculate_time_and_amount(frm, cdt, cdn);
  },

  time_logs_add: function (frm, cdt, cdn) {
    if (frm.doc.project) {
      frappe.model.set_value(cdt, cdn, "project", frm.doc.project);
    }
  },

  hours: function (frm, cdt, cdn) {
    calculate_end_time(frm, cdt, cdn);
    calculate_billing_costing_amount(frm, cdt, cdn);
    calculate_time_and_amount(frm, cdt, cdn);
  },

  custom_reason: function (frm, cdt, cdn) {
    frappe.model.set_value(cdt, cdn, "custom_over_time_hours", 0);
    frappe.model.set_value(cdt, cdn, "custom_regular_hours", 0);
    frappe.model.set_value(cdt, cdn, "hours", 0.0004);
    frappe.model.set_value(cdt, cdn, "custom_total_hrs", 0.0004);
  },

  custom_over_time_hours: function (frm, cdt, cdn) {
    calculate_time_and_amount(frm, cdt, cdn);
  },

  custom_regular_hours: function (frm, cdt, cdn) {
    const child = locals[cdt][cdn];
    const hours = child.custom_regular_hours ? child.custom_regular_hours : 0;
    frappe.model.set_value(cdt, cdn, "hours", hours);
    calculate_time_and_amount(frm, cdt, cdn);
  },

  billing_hours: function (frm, cdt, cdn) {
    calculate_billing_costing_amount(frm, cdt, cdn);
    calculate_time_and_amount(frm, cdt, cdn);
  },

  billing_rate: function (frm, cdt, cdn) {
    calculate_billing_costing_amount(frm, cdt, cdn);
    calculate_time_and_amount(frm, cdt, cdn);
  },

  costing_rate: function (frm, cdt, cdn) {
    calculate_billing_costing_amount(frm, cdt, cdn);
    calculate_time_and_amount(frm, cdt, cdn);
  },

  is_billable: function (frm, cdt, cdn) {
    update_billing_hours(frm, cdt, cdn);
    update_time_rates(frm, cdt, cdn);
    calculate_billing_costing_amount(frm, cdt, cdn);
    calculate_time_and_amount(frm, cdt, cdn);
  },

  activity_type: function (frm, cdt, cdn) {
    if (!frappe.get_doc(cdt, cdn).activity_type) return;

    frappe.call({
      method: "erpnext.projects.doctype.timesheet.timesheet.get_activity_cost",
      args: {
        employee: frm.doc.employee,
        activity_type: frm.selected_doc.activity_type,
        currency: frm.doc.currency,
      },
      callback: function (r) {
        if (r.message) {
          frappe.model.set_value(
            cdt,
            cdn,
            "billing_rate",
            r.message["billing_rate"]
          );
          frappe.model.set_value(
            cdt,
            cdn,
            "costing_rate",
            r.message["costing_rate"]
          );
          calculate_billing_costing_amount(frm, cdt, cdn);
        }
      },
    });
    calculate_time_and_amount(frm, cdt, cdn);
  },
});

var calculate_end_time = function (frm, cdt, cdn) {
  let child = locals[cdt][cdn];

  if (!child.from_time) {
    // if from_time value is not available then set the current datetime
    frappe.model.set_value(
      cdt,
      cdn,
      "from_time",
      frappe.datetime.get_datetime_as_string()
    );
  }

  let d = moment(child.from_time);
  if (child.hours) {
    d.add(child.hours, "hours");
    frm._setting_hours = true;
    frappe.model
      .set_value(
        cdt,
        cdn,
        "to_time",
        d.format(frappe.defaultDatetimeFormat.toString())
      )
      .then(() => {
        frm._setting_hours = false;
      });
  } else {
    d.add(1, "seconds");
    frm._setting_hours = true;
    frappe.model
      .set_value(
        cdt,
        cdn,
        "to_time",
        d.format(frappe.defaultDatetimeFormat.toString())
      )
      .then(() => {
        frm._setting_hours = false;
      });
  }
};

var update_billing_hours = function (frm, cdt, cdn) {
  let child = frappe.get_doc(cdt, cdn);
  if (!child.is_billable) {
    frappe.model.set_value(cdt, cdn, "billing_hours", 0.0);
  } else {
    // bill all hours by default
    frappe.model.set_value(cdt, cdn, "billing_hours", child.hours);
  }
};

var update_time_rates = function (frm, cdt, cdn) {
  let child = frappe.get_doc(cdt, cdn);
  if (!child.is_billable) {
    frappe.model.set_value(cdt, cdn, "billing_rate", 0.0);
  }
};

var calculate_billing_costing_amount = function (frm, cdt, cdn) {
  let row = frappe.get_doc(cdt, cdn);
  let billing_amount = 0.0;
  let base_billing_amount = 0.0;
  let exchange_rate = flt(frm.doc.exchange_rate);
  frappe.model.set_value(
    cdt,
    cdn,
    "base_billing_rate",
    flt(row.billing_rate) * exchange_rate
  );
  frappe.model.set_value(
    cdt,
    cdn,
    "base_costing_rate",
    flt(row.costing_rate) * exchange_rate
  );
  if (row.billing_hours && row.is_billable) {
    base_billing_amount = flt(row.billing_hours) * flt(row.base_billing_rate);
    billing_amount = flt(row.billing_hours) * flt(row.billing_rate);
  }

  frappe.model.set_value(cdt, cdn, "base_billing_amount", base_billing_amount);
  frappe.model.set_value(
    cdt,
    cdn,
    "base_costing_amount",
    flt(row.base_costing_rate) * flt(row.hours)
  );
  frappe.model.set_value(cdt, cdn, "billing_amount", billing_amount);
  frappe.model.set_value(
    cdt,
    cdn,
    "costing_amount",
    flt(row.costing_rate) * flt(row.hours)
  );
};

var calculate_time_and_amount = function (frm, cdt, cdn) {
  let child = locals[cdt][cdn];
  let tl = frm.doc.time_logs || [];
  let total_reguler_hr = 0;
  let total_overtime_hr = 0;
  const total_hours_val =
    child.custom_over_time_hours > 0
      ? child.hours + child.custom_over_time_hours
      : child.hours
      ? child.hours
      : 0;
  frappe.model.set_value(cdt, cdn, "custom_total_hrs", total_hours_val);
  for (var i = 0; i < tl.length; i++) {
    if (tl[i].hours) {
      total_reguler_hr += tl[i].hours;
      total_overtime_hr += tl[i].custom_over_time_hours;
    }
  }

  frm.set_value("total_regular_hours", total_reguler_hr);
  frm.set_value("total_overtime_hours", total_overtime_hr);
  frm.set_value("total_hours", total_reguler_hr + total_overtime_hr);
  //   frm.set_value("total_billable_amount", total_billable_amount);
  //   frm.set_value("total_costing_amount", total_costing_amount);
};
