import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import require_client_or_redirect, get_client_projects

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "progress"
	context.title = "Progress Updates"

	prop_names = frappe.get_all("Property", filters={"primary_client": client.name}, pluck="name", ignore_permissions=True)
	projects = get_client_projects(client.name)
	project_names = [p.name for p in projects]

	updates = []
	if project_names:
		project_wide = frappe.get_all(
			"Progress Update",
			filters=[["project", "in", project_names], ["visibility_mode", "=", "Project-wide"]],
			fields=["name", "title", "update_date", "project", "description", "visibility_mode"],
			order_by="update_date desc",
			ignore_permissions=True,
		)
		updates += project_wide

	if prop_names:
		per_unit = frappe.get_all(
			"Progress Update",
			filters=[["property", "in", prop_names], ["visibility_mode", "=", "Per-unit"]],
			fields=["name", "title", "update_date", "project", "description", "visibility_mode"],
			order_by="update_date desc",
			ignore_permissions=True,
		)
		updates += per_unit

	# Sort by date and deduplicate
	seen = set()
	unique = []
	for u in sorted(updates, key=lambda x: x.update_date or "", reverse=True):
		if u.name not in seen:
			seen.add(u.name)
			photos = frappe.get_all(
				"Progress Photo",
				filters={"parent": u.name},
				fields=["image", "caption"],
				ignore_permissions=True,
			)
			u.photos = photos
			if u.project:
				u.project_name = frappe.db.get_value("Estate Project", u.project, "project_name")
			unique.append(u)

	context.updates = unique
