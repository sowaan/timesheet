from frappe import _


def get_data():
	return {
		"fieldname": "custom_auto_timesheet_creation",
		"non_standard_fieldnames": {
			"Timesheet": "custom_auto_timesheet_creation",
		},
		"transactions": [{"items": ["Timesheet"]}],
	}
