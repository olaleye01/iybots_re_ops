# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentPlan(Document):
	def validate(self):
		self.populate_customer()
		self.calculate_totals()

	def populate_customer(self):
		"""Auto-fill Customer from the linked Opportunity's Lead."""
		if not self.opportunity or self.customer:
			return

		opp = frappe.db.get_value(
			"Opportunity", self.opportunity, ["opportunity_from", "party_name"], as_dict=True
		)
		if not opp:
			return

		if opp.opportunity_from == "Lead" and opp.party_name:
			from iybots_re_ops.iybots_real_estate_ops.crm_hooks import get_or_create_customer_from_lead
			self.customer = get_or_create_customer_from_lead(opp.party_name)
		elif opp.opportunity_from == "Customer" and opp.party_name:
			self.customer = opp.party_name

	def calculate_totals(self):
		"""Compute total_paid and total_outstanding from milestones."""
		total_paid = 0
		for milestone in self.milestones:
			if milestone.status == "Paid":
				total_paid += milestone.amount or 0
		self.total_paid = total_paid
		self.total_outstanding = (self.total_amount or 0) - total_paid


def mark_overdue_milestones():
	"""Daily scheduled task: mark pending milestones past due_date as Overdue."""
	from frappe.utils import today

	overdue = frappe.db.sql(
		"""
		UPDATE `tabPayment Milestone`
		SET status = 'Overdue'
		WHERE status = 'Pending'
		AND due_date < %s
		""",
		(today(),),
	)
	frappe.db.commit()

	# Recalculate totals for affected Payment Plans
	affected_plans = frappe.db.sql(
		"""
		SELECT DISTINCT parent FROM `tabPayment Milestone`
		WHERE status = 'Overdue'
		AND due_date < %s
		""",
		(today(),),
		as_dict=True,
	)

	for plan in affected_plans:
		try:
			doc = frappe.get_doc("Payment Plan", plan.parent)
			doc.calculate_totals()
			doc.db_update()
		except Exception:
			frappe.log_error(f"Error recalculating Payment Plan {plan.parent}")
