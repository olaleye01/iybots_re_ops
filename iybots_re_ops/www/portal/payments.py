import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import require_client_or_redirect, fmt

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "payments"
	context.title = "Payment Schedule"

	prop_names = frappe.get_all(
		"Property", filters={"primary_client": client.name}, pluck="name", ignore_permissions=True
	)

	plans = []
	if prop_names:
		raw_plans = frappe.get_all(
			"Payment Plan",
			filters={"property": ["in", prop_names]},
			fields=["name", "plan_title", "property", "total_amount", "total_paid", "total_outstanding", "status"],
			ignore_permissions=True,
		)
		for plan in raw_plans:
			plan.total_amount_fmt = fmt(plan.total_amount or 0)
			plan.total_paid_fmt = fmt(plan.total_paid or 0)
			plan.total_outstanding_fmt = fmt(plan.total_outstanding or 0)
			plan.prop_name = frappe.db.get_value("Property", plan.property, "property_name") if plan.property else None

			milestones = frappe.get_all(
				"Payment Milestone",
				filters={"parent": plan.name},
				fields=["due_date", "amount", "status", "payment_ref"],
				order_by="due_date asc",
				ignore_permissions=True,
			)
			for m in milestones:
				m.amount_fmt = fmt(m.amount or 0)
			plan.milestones = milestones
			plans.append(plan)

	context.plans = plans
