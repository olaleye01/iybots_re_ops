import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import require_client_or_redirect

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "documents"
	context.title = "Documents"

	docs = frappe.get_all(
		"Client Document",
		filters={"client": client.name},
		fields=["name", "document_type", "uploaded_on", "property", "file", "notes"],
		order_by="uploaded_on desc",
		ignore_permissions=True,
	)
	for d in docs:
		if d.property:
			d.prop_name = frappe.db.get_value("Property", d.property, "property_name")
	context.documents = docs
