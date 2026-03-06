import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import require_client_or_redirect, fmt

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "documents"
	context.title = "Receipts"

	receipts = frappe.get_all(
		"Receipt",
		filters={"client": client.name},
		fields=["name", "receipt_date", "amount", "property", "file"],
		order_by="receipt_date desc",
		ignore_permissions=True,
	)
	for r in receipts:
		r.amount_fmt = fmt(r.amount or 0)
		if r.property:
			r.prop_name = frappe.db.get_value("Property", r.property, "property_name")
	context.receipts = receipts
