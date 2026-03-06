import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import (
	require_client_or_redirect, get_client_properties,
	get_payment_summary, fmt,
)

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "dashboard"
	context.title = "Dashboard"

	props = get_client_properties(client.name)
	summary = get_payment_summary(client.name)

	context.property_count = len(props)
	context.total_paid = fmt(summary["total_paid"])
	context.total_outstanding = fmt(summary["total_outstanding"])
	context.next_due = summary["next_due"]
	if context.next_due:
		context.next_due.amount_fmt = fmt(context.next_due.amount or 0)

	# Latest progress update across client's projects
	from iybots_re_ops.iybots_real_estate_ops.portal_utils import get_client_projects
	projects = get_client_projects(client.name)
	project_names = [p.name for p in projects]
	prop_names = [p.name for p in props]

	latest_updates = []
	if project_names:
		latest_updates = frappe.get_all(
			"Progress Update",
			filters=[
				["project", "in", project_names],
				["visibility_mode", "=", "Project-wide"],
			],
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
	if context.latest_update:
		photos = frappe.get_all(
			"Progress Photo",
			filters={"parent": context.latest_update.name},
			fields=["image"],
			limit=1,
			ignore_permissions=True,
		)
		context.latest_update.thumb = photos[0].image if photos else None
