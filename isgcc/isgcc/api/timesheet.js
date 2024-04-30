// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Timesheet", {
  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      if (
        frm.doc.per_billed < 100 &&
        frm.doc.total_billable_hours &&
        frm.doc.total_billable_hours > frm.doc.total_billed_hours
      ) {
        frm.remove_custom_button(__("Create Sales Invoice"));
        frm.add_custom_button(__("Make Sales Invoice"), function () {
          frm.trigger("make_invoices");
        });
      }
    }
  },
  make_invoices: function (frm) {
    let fields = [
      {
        fieldtype: "Link",
        label: __("Item Code"),
        fieldname: "item_code",
        options: "Item",
        mandatory: 1,
      },
    ];

    if (!frm.doc.customer) {
      fields.push({
        fieldtype: "Link",
        label: __("Customer"),
        fieldname: "customer",
        options: "Customer",
        default: frm.doc.customer,
      });
    }

    if (frm.doc.time_logs) {
      fields.push({
        label: "Time Sheets",
        fieldname: "time_logs",
        fieldtype: "Table",
        cannot_add_rows: true,
        cannot_delete_rows: true,
        read_only: 1,
        in_place_edit: true,
        data: frm.doc.time_logs.filter((e) => {
          if (e.sales_invoice == null) {
            e.__checked = 1;
            return e;
          }
        }),
        fields: [
          {
            fieldname: "activity_type",
            fieldtype: "Link",
            in_list_view: 1,
            label: "Activity Type",
            options: "Activity Type",
          },
          {
            fieldname: "from_time",
            fieldtype: "Datetime",
            in_list_view: 1,
            label: "From Time",
          },
          {
            fieldname: "to_time",
            fieldtype: "Datetime",
            in_list_view: 1,
            label: "To Time",
          },
          {
            fieldname: "hours",
            fieldtype: "Float",
            in_list_view: 1,
            label: "Hrs",
          },
          {
            fieldname: "custom_over_time",
            fieldtype: "Check",
            in_list_view: 1,
            label: "Over Time",
          },
        ],
      });
    }

    let dialog = new frappe.ui.Dialog({
      title: __("Create Sales Invoice"),
      fields: fields,
      size: "large",
    });

    dialog.set_primary_action(__("Create Sales Invoice"), () => {
      var args = dialog.get_values();
      if (!args) return;
      let selectedTimeSheet = args.time_logs.filter((ele) => {
        if (ele.__checked === 1) {
          return ele;
        }
      });
      dialog.hide();
      return frappe.call({
        type: "GET",
        method: "isgcc.overrides.customer_sales_invoice.make_sales_invoice",
        args: {
          source_name: frm.doc.name,
          item_code: args.item_code,
          customer: frm.doc.customer || args.customer,
          currency: frm.doc.currency,
          timesheet_log: selectedTimeSheet,
        },
        freeze: true,
        callback: function (r) {
          if (!r.exc) {
            frappe.model.sync(r.message);
            frappe.set_route("Form", r.message.doctype, r.message.name);
          }
        },
      });
    });
    dialog.show();
  },
});
