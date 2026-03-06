import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import require_client_or_redirect, fmt

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "units"

	prop_name = frappe.form_dict.get("name")
	if not prop_name:
		frappe.local.flags.redirect_location = "/portal/units"
		raise frappe.Redirect

	prop = frappe.db.get_value(
		"Property",
		{"name": prop_name, "primary_client": client.name},
		["name", "property_name", "property_type", "status", "location", "price",
		 "developer", "description", "images", "project", "assigned_agent"],
		as_dict=True,
		ignore_permissions=True,
	)

	if not prop:
		frappe.throw("Property not found or access denied.", frappe.PermissionError)

	prop.price_fmt = fmt(prop.price or 0)
	if prop.project:
		prop.project_doc = frappe.db.get_value(
			"Estate Project", prop.project,
			["project_name", "location", "status", "description", "banner_image"],
			as_dict=True,
		)
	if prop.assigned_agent:
		prop.agent_name = frappe.db.get_value("User", prop.assigned_agent, "full_name")
		prop.agent_email = prop.assigned_agent

	context.prop = prop
	context.title = prop.property_name
