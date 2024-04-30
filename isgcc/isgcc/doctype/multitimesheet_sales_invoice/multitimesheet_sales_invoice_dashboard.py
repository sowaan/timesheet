from frappe import _


def get_data():
	return {
		"fieldname": "custom_reference",
		"transactions": [{"label": _("References"), "items": ["Sales Invoice"]}],
	}
