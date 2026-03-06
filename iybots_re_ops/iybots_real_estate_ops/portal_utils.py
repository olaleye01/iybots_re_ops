# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt
#
# Shared utilities for all client portal pages.
# Auth pattern: call require_client_or_redirect() first in every get_context().

import frappe
from frappe import _
from frappe.utils import fmt_money


def require_client_or_redirect():
	"""
	Verify the current session user is an authenticated portal client.
	Returns the Client doc. Redirects to /login if guest, raises 403 if no client found.
	"""
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/portal/login?redirect-to=/portal"
		raise frappe.Redirect

	client_name = frappe.db.get_value("Client", {"linked_user": frappe.session.user, "is_active": 1})
	if not client_name:
		frappe.throw(_("You do not have access to the client portal."), frappe.PermissionError)

	return frappe.get_doc("Client", client_name)


def get_client_properties(client_name):
	"""Return all Property records linked to this client."""
	return frappe.get_all(
		"Property",
		filters={"primary_client": client_name},
		fields=["name", "property_name", "property_type", "status", "location", "price", "project", "assigned_agent", "images"],
		ignore_permissions=True,
	)


def get_client_projects(client_name):
	"""Return distinct Estate Projects for this client's properties."""
	props = frappe.get_all("Property", filters={"primary_client": client_name}, pluck="project", ignore_permissions=True)
	projects = [p for p in props if p]
	if not projects:
		return []
	return frappe.get_all(
		"Estate Project",
		filters={"name": ["in", projects]},
		fields=["name", "project_name", "location", "status", "banner_image", "description"],
		ignore_permissions=True,
	)


def get_payment_summary(client_name):
	"""Return total_paid, total_outstanding, and next due milestone for this client."""
	prop_names = frappe.get_all("Property", filters={"primary_client": client_name}, pluck="name", ignore_permissions=True)
	if not prop_names:
		return {"total_paid": 0, "total_outstanding": 0, "next_due": None}

	plans = frappe.get_all(
		"Payment Plan",
		filters={"property": ["in", prop_names]},
		fields=["name", "total_paid", "total_outstanding"],
		ignore_permissions=True,
	)

	total_paid = sum(p.total_paid or 0 for p in plans)
	total_outstanding = sum(p.total_outstanding or 0 for p in plans)

	# Find next upcoming Due/Overdue milestone
	if plans:
		plan_names = [p.name for p in plans]
		next_due = frappe.db.sql("""
			SELECT pm.due_date, pm.amount, pm.status, pp.name as plan_name
			FROM `tabPayment Milestone` pm
			JOIN `tabPayment Plan` pp ON pm.parent = pp.name
			WHERE pm.parent IN %(plans)s
			  AND pm.status IN ('Pending', 'Overdue')
			ORDER BY pm.due_date ASC
			LIMIT 1
		""", {"plans": plan_names}, as_dict=True)
		next_due = next_due[0] if next_due else None
	else:
		next_due = None

	return {
		"total_paid": total_paid,
		"total_outstanding": total_outstanding,
		"next_due": next_due,
	}


def fmt(amount):
	return fmt_money(amount, currency="NGN")
