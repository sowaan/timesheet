from frappe import _


def get_data():
	return {
		"fieldname": "mobilization",
		"non_standard_fieldnames": {
			"Auto Timesheet Creation": "mobilization",
		},
		"transactions": [{"items": ["Auto Timesheet Creation"]}],
	}
