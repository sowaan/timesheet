// Copyright (c) 2024, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Mobilization", {
  refresh(frm) {
    frm.set_query("sales_order", function () {
      return {
        filters: [
          ["customer", "=", frm.doc.customer],
          ["Sales Order Item", "asset", "=", frm.doc.asset],
        ],
      };
    });
  },

  start_date(frm) {
    frm.trigger("validate_employee_and_asset");
  },
  end_date(frm) {
    frm.trigger("validate_employee_and_asset");
  },
  validate_employee_and_asset(frm) {
    if (frm.doc.start_date && frm.doc.end_date) {
      frappe.call({
        method:
          "isgcc.isgcc.doctype.mobilization.mobilization.get_mobilization_list",
        args: {
          start_date: frm.doc.start_date,
          end_date: frm.doc.end_date,
        },
        callback: function (response) {
          if (response.message) {
            frm.set_value("employee", "");
            frm.set_value("asset", "");
            frm.set_query("asset", function () {
              return {
                filters: [["name", "not in", response.message.assets]],
              };
            });
            // frm.set_query("employee", function () {
            //   return {
            //     filters: [["name", "not in", response.message.employees]],
            //   };
            // });
          }
        },
      });
    }
  },
});
