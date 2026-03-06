# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt
#
# Permission query conditions for row-level security.
# RE Agent role is restricted to records they own, enforced at the DB query level.
#
# Enforcement method:
#   - Lead:               lead_owner == session.user
#   - Opportunity:        opportunity_owner == session.user
#   - Commission Record:  agent == session.user  (field auto-populated from opportunity_owner)
#   - Agent Check-in:     agent == session.user  (defaults to current user on create)

import frappe


def _is_agent(user):
	return "RE Agent" in frappe.get_roles(user)


# ── Lead ─────────────────────────────────────────────────────────────────────

def get_permission_query_conditions_for_lead(user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		return f"`tabLead`.`lead_owner` = {frappe.db.escape(user)}"
	return None


def has_permission_for_lead(doc, ptype, user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		if ptype == "create":
			return True  # new doc has no lead_owner yet; before_insert enforces ownership
		return doc.lead_owner == user
	return True


# ── Opportunity ───────────────────────────────────────────────────────────────

def get_permission_query_conditions_for_opportunity(user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		return f"`tabOpportunity`.`opportunity_owner` = {frappe.db.escape(user)}"
	return None


def has_permission_for_opportunity(doc, ptype, user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		if ptype == "create":
			return True  # new doc has no opportunity_owner yet; before_insert enforces ownership
		return doc.opportunity_owner == user
	return True


# ── Commission Record ─────────────────────────────────────────────────────────

def get_permission_query_conditions_for_commission_record(user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		return f"`tabCommission Record`.`agent` = {frappe.db.escape(user)}"
	return None


def has_permission_for_commission_record(doc, ptype, user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		return doc.agent == user
	return True


# ── Agent Check-in ────────────────────────────────────────────────────────────

def get_permission_query_conditions_for_agent_check_in(user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		return f"`tabAgent Check-in`.`agent` = {frappe.db.escape(user)}"
	return None


def has_permission_for_agent_check_in(doc, ptype, user):
	if not user:
		user = frappe.session.user
	if _is_agent(user):
		return doc.agent == user
	return True
