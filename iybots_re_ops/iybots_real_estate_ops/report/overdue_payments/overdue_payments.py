# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Payment Plan"),
			"fieldname": "payment_plan",
			"fieldtype": "Link",
			"options": "Payment Plan",
			"width": 150,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{
			"label": _("Opportunity"),
			"fieldname": "opportunity",
			"fieldtype": "Link",
			"options": "Opportunity",
			"width": 150,
		},
		{
			"label": _("Due Date"),
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Amount Due"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("Notes"),
			"fieldname": "notes",
			"fieldtype": "Data",
			"width": 200,
		},
	]


def get_data(filters):
	query = """
		SELECT
			pm.parent AS payment_plan,
			pp.customer,
			pp.opportunity,
			pm.due_date,
			pm.amount,
			pm.notes
		FROM
			`tabPayment Milestone` pm
		INNER JOIN `tabPayment Plan` pp ON pm.parent = pp.name
		WHERE
			pm.status = 'Overdue'
	"""

	if filters and filters.get("customer"):
		query += f" AND pp.customer = {frappe.db.escape(filters.get('customer'))}"

	query += " ORDER BY pm.due_date ASC"

	return frappe.db.sql(query, as_dict=True)
