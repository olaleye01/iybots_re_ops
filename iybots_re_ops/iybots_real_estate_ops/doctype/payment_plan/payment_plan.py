# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentPlan(Document):
	def validate(self):
		self.calculate_totals()

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
