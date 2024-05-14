app_name = "isgcc"
app_title = "ISGCC"
app_publisher = "Sowaan"
app_description = "Intelligent Systems General Contracting Company"
app_email = "support@sowaan.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/isgcc/css/isgcc.css"
# app_include_js = "/assets/isgcc/js/isgcc.js"

# include js, css files in header of web template
# web_include_css = "/assets/isgcc/css/isgcc.css"
# web_include_js = "/assets/isgcc/js/isgcc.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "isgcc/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Timesheet": "isgcc/api/timesheet.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "isgcc/public/icons.svg"

# Home Pages
# ----------

fixtures = [
	{
        "doctype":"Custom Field",
		"filters":[
			[
				"fieldname",
                "in",
                (   
                "custom_asset", "custom_auto_timesheet_creation", "custom_mobilization_status", 
				"custom_asset_type", "custom_asset_name", "custom_holiday", 
				"custom_cost_center", "custom_project", "custom_regular_hours", 
				"custom_over_time_hours", "custom_over_time", "custom_parent_name",
                "custom_total_hrs", "custom_reason", "custom_sales_order", "custom_overtime",
                "custom_purchase_invoice", "custom_purchase_order", "custom_supplier", 
                "custom_total_regular_hours", "custom_total_over_time_hours", "custom_reference"
				)
			]
		]
	}
]


# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "isgcc.utils.jinja_methods",
#	"filters": "isgcc.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "isgcc.install.before_install"
# after_install = "isgcc.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "isgcc.uninstall.before_uninstall"
# after_uninstall = "isgcc.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "isgcc.utils.before_app_install"
# after_app_install = "isgcc.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "isgcc.utils.before_app_uninstall"
# after_app_uninstall = "isgcc.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "isgcc.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Purchase Invoice": "isgcc.overrides.timesheet_purchase_invoice.TimesheetPurchaseInvoice"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"Purchase Invoice": {
# 		# "on_update": "method",
# 		"on_cancel": "isgcc.overrides.timesheet_purchase_invoice.timesheet_purchase_invoice.on_cancel",
# 		# "on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"isgcc.tasks.all"
#	],
#	"daily": [
#		"isgcc.tasks.daily"
#	],
#	"hourly": [
#		"isgcc.tasks.hourly"
#	],
#	"weekly": [
#		"isgcc.tasks.weekly"
#	],
#	"monthly": [
#		"isgcc.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "isgcc.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.projects.doctype.timesheet.timesheet.make_sales_invoice": "isgcc.overrides.customer_sales_invoice.make_sales_invoice",
	"erpnext.projects.doctype.timesheet.timesheet.get_timesheet_detail_rate": "isgcc.overrides.customer_sales_invoice.get_timesheet_detail_rate"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "isgcc.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["isgcc.utils.before_request"]
# after_request = ["isgcc.utils.after_request"]

# Job Events
# ----------
# before_job = ["isgcc.utils.before_job"]
# after_job = ["isgcc.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"isgcc.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
#	"Logging DocType Name": 30  # days to retain logs
# }

