# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt
#
# Doc event hooks for CRM (Lead, Opportunity) enforcing agent ownership rules.

import frappe
from frappe import _


def _is_agent(user=None):
	user = user or frappe.session.user
	return "RE Agent" in frappe.get_roles(user)


# ── Customer helpers ──────────────────────────────────────────────────────────

def get_or_create_customer_from_lead(lead_name):
	"""
	Find an existing Customer created from this Lead, or create one.
	Returns the Customer name (ID).
	"""
	lead = frappe.get_doc("Lead", lead_name)

	# Check if a Customer already exists for this lead (by matching lead_name field or customer_name)
	existing = frappe.db.get_value("Customer", {"lead_name": lead_name})
	if not existing:
		# Fallback: match by customer_name == lead.lead_name
		existing = frappe.db.get_value("Customer", {"customer_name": lead.lead_name})

	if existing:
		return existing

	# Create a new Customer from the Lead's data
	customer = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": lead.lead_name,
		"customer_type": "Company" if lead.get("company_name") else "Individual",
		"lead_name": lead_name,
		"email_id": lead.get("email_id") or "",
		"mobile_no": lead.get("mobile_no") or lead.get("phone") or "",
	})
	customer.insert(ignore_permissions=True)
	frappe.db.set_value("Lead", lead_name, "status", "Converted")
	return customer.name


# ── Opportunity hooks ─────────────────────────────────────────────────────────

def opportunity_before_insert(doc, method):
	"""
	When an RE Agent creates an Opportunity:
	  1. Auto-set opportunity_owner to the current user.
	  2. If a Lead is linked, ensure the agent owns that Lead.
	"""
	if not _is_agent():
		return

	doc.opportunity_owner = frappe.session.user

	if doc.opportunity_from == "Lead" and doc.party_name:
		lead_owner = frappe.db.get_value("Lead", doc.party_name, "lead_owner")
		if lead_owner != frappe.session.user:
			frappe.throw(
				_("You can only create an Opportunity from a Lead that you own.")
			)


def opportunity_on_closed_won(doc, method):
	"""Auto-create a Customer when an Opportunity reaches Closed Won."""
	if doc.sales_stage != "Closed Won":
		return
	if doc.opportunity_from == "Lead" and doc.party_name:
		get_or_create_customer_from_lead(doc.party_name)
