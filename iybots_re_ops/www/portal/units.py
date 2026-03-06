import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import require_client_or_redirect, get_client_properties, fmt

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "units"
	context.title = "My Units"

	props = get_client_properties(client.name)
	for p in props:
		p.price_fmt = fmt(p.price or 0)
		if p.project:
			p.project_name = frappe.db.get_value("Estate Project", p.project, "project_name")
	context.properties = props
