import frappe

no_cache = 1


def get_context(context):
	# Already logged-in portal users go straight to the portal
	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = "/portal"
		raise frappe.Redirect

	context.title = "Sign In — Iybots Real Estate"
	context.redirect_to = frappe.form_dict.get("redirect-to", "/portal")
