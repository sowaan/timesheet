// Copyright (c) 2024, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Mobilization", {
  refresh(frm) {
    // if document is new then set asset and sales order value is not set
    if (frm.doc.__islocal) {
      frm.set_value("asset", "");
      frm.set_value("sales_order", "");
      frm.trigger("validate_employee_and_asset");
    }
    frm.set_query("sales_order", function () {
      return {
        filters: [
          ["customer", "=", frm.doc.customer],
          ["Sales Order Item", "asset", "=", frm.doc.asset],
        ],
      };
    });
    if (frm.doc.docstatus === 1 && !frm.doc.demobilized) {
      // make demobile button
      frm.add_custom_button(__("De-Mobilize"), function () {
        frappe.call({
          method:
            "isgcc.isgcc.doctype.mobilization.mobilization.demobilize_asset",
          args: {
            name: frm.doc.name,
            asset: frm.doc.asset,
          },
          callback: function (response) {
            if (response.message) {
              frappe.msgprint(response.message);
              frm.reload_doc();
            }
          },
        });
      });
    }
  },

  customer(frm) {
    frm.set_value("sales_order", "");
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
            // frm.set_value("employee", "");
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
