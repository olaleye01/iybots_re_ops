import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import (
	require_client_or_redirect, get_client_properties,
	get_client_projects, get_payment_summary, fmt,
)

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "dashboard"
	context.title = "Dashboard"

	props = get_client_properties(client.name)
	prop_names = [p.name for p in props]
	summary = get_payment_summary(client.name)

	context.property_count = len(props)
	context.total_paid = fmt(summary["total_paid"])
	context.total_outstanding = fmt(summary["total_outstanding"])
	context.next_due = summary["next_due"]
	if context.next_due:
		context.next_due.amount_fmt = fmt(context.next_due.amount or 0)

	# Percentage paid (for Total Paid card sub-text)
	plans = frappe.get_all(
		"Payment Plan",
		filters={"property": ["in", prop_names]} if prop_names else {"name": "__never__"},
		fields=["total_amount", "total_paid"],
		ignore_permissions=True,
	) if prop_names else []
	total_amount = sum(p.total_amount or 0 for p in plans)
	total_paid_raw = summary["total_paid"]
	context.total_paid_pct = round(total_paid_raw / total_amount * 100) if total_amount else 0
	context.total_amount_fmt = fmt(total_amount)

	# Upcoming milestones (next 5) for the schedule table
	upcoming = []
	if prop_names:
		plan_names = [p.name for p in plans]
		if plan_names:
			upcoming = frappe.db.sql("""
				SELECT pm.due_date, pm.amount, pm.status,
				       pp.plan_title, prop.property_name
				FROM `tabPayment Milestone` pm
				JOIN `tabPayment Plan` pp ON pm.parent = pp.name
				JOIN `tabProperty` prop ON pp.property = prop.name
				WHERE pm.parent IN %(plans)s
				  AND pm.status IN ('Pending', 'Overdue')
				ORDER BY pm.due_date ASC
				LIMIT 5
			""", {"plans": plan_names}, as_dict=True)
			for m in upcoming:
				m.amount_fmt = fmt(m.amount or 0)
	context.upcoming_milestones = upcoming

	# Latest progress update
	projects = get_client_projects(client.name)
	project_names = [p.name for p in projects]

	latest_updates = []
	if project_names:
		latest_updates = frappe.get_all(
			"Progress Update",
			filters=[["project", "in", project_names], ["visibility_mode", "=", "Project-wide"]],
			fields=["name", "title", "update_date", "project", "description"],
			order_by="update_date desc",
			limit=1,
			ignore_permissions=True,
		)
	if not latest_updates and prop_names:
		latest_updates = frappe.get_all(
			"Progress Update",
			filters=[["property", "in", prop_names], ["visibility_mode", "=", "Per-unit"]],
			fields=["name", "title", "update_date", "project", "description"],
			order_by="update_date desc",
			limit=1,
			ignore_permissions=True,
		)

	context.latest_update = latest_updates[0] if latest_updates else None
