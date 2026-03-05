# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_weekdays, add_days, getdate, today


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
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100,
		},
	]


def get_data(filters):
	start_of_week = getdate(add_days(today(), -getdate(today()).weekday()))
	end_of_week = getdate(add_days(start_of_week, 6))

	query = """
		SELECT
			pm.parent AS payment_plan,
			pp.customer,
			pp.opportunity,
			pm.due_date,
			pm.amount,
			pm.status
		FROM
			`tabPayment Milestone` pm
		INNER JOIN `tabPayment Plan` pp ON pm.parent = pp.name
		WHERE
			pm.due_date BETWEEN %s AND %s
			AND pm.status != 'Paid'
	"""

	args = [start_of_week, end_of_week]

	query += " ORDER BY pm.due_date ASC"

	return frappe.db.sql(query, args, as_dict=True)
