import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	check_if_return_invoice_linked_with_payment_entry,
	get_total_in_party_account_currency,
	is_overdue,
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)


class TimesheetPurchaseInvoice(PurchaseInvoice):
    def on_cancel(self):
        self.unlinked_purchase_invoice_in_timesheets()
        check_if_return_invoice_linked_with_payment_entry(self)

        super(PurchaseInvoice, self).on_cancel()

        self.check_on_hold_or_closed_status()

        if self.is_return and not self.update_billed_amount_in_purchase_order:
            # NOTE status updating bypassed for is_return
            self.status_updater = []

        self.update_status_updater_args()
        self.update_prevdoc_status()

        if not self.is_return:
            self.update_billing_status_for_zero_amount_refdoc("Purchase Receipt")
            self.update_billing_status_for_zero_amount_refdoc("Purchase Order")

        self.update_billing_status_in_pr()

        # Updating stock ledger should always be called after updating prevdoc status,
        # because updating ordered qty in bin depends upon updated ordered qty in PO
        if self.update_stock == 1:
            self.update_stock_ledger()
            self.delete_auto_created_batches()

            if self.is_old_subcontracting_flow:
                self.set_consumed_qty_in_subcontract_order()

        self.make_gl_entries_on_cancel()

        if self.update_stock == 1:
            self.repost_future_sle_and_gle()

        if (
            frappe.db.get_single_value("Buying Settings", "project_update_frequency") == "Each Transaction"
        ):
            self.update_project()
        self.db_set("status", "Cancelled")

        unlink_inter_company_doc(self.doctype, self.name, self.inter_company_invoice_reference)
        self.ignore_linked_doctypes = (
            "GL Entry",
            "Stock Ledger Entry",
            "Repost Item Valuation",
            "Repost Payment Ledger",
            "Repost Payment Ledger Items",
            "Repost Accounting Ledger",
            "Repost Accounting Ledger Items",
            "Unreconcile Payment",
            "Unreconcile Payment Entries",
            "Payment Ledger Entry",
            "Tax Withheld Vouchers",
            "Serial and Batch Bundle",
        )
        self.update_advance_tax_references(cancel=1)


    def unlinked_purchase_invoice_in_timesheets(self):
        print(self.name, "I want to check purchase ivonice name")
        # frappe.get_all("")
        doc_list = frappe.get_all("Timesheet Detail", filters=[["custom_purchase_invoice", "=", self.name]])
        for doc in doc_list:
            frappe.db.set_value("Timesheet Detail", doc.name, "custom_purchase_invoice", "")