# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CommissionRecord(Document):
	def validate(self):
		self.fetch_deal_value()
		self.populate_agent()
		self.calculate_commission()
		self.validate_splits()

	def populate_agent(self):
		"""Set agent from linked Opportunity's opportunity_owner."""
		if self.opportunity and not self.agent:
			self.agent = frappe.db.get_value(
				"Opportunity", self.opportunity, "opportunity_owner"
			)

	def fetch_deal_value(self):
		"""Fetch deal value from linked Opportunity."""
		if self.opportunity:
			self.deal_value = frappe.db.get_value(
				"Opportunity", self.opportunity, "opportunity_amount"
			) or 0

	def calculate_commission(self):
		"""Calculate commission amount and split amounts."""
		self.commission_amount = (self.deal_value or 0) * (self.commission_percent or 0) / 100

		for split in self.splits:
			split.split_amount = self.commission_amount * (split.split_percent or 0) / 100

	def validate_splits(self):
		"""Ensure split percentages total 100%."""
		if not self.splits:
			return

		total_percent = sum(split.split_percent or 0 for split in self.splits)
		if abs(total_percent - 100) > 0.01:
			frappe.throw(
				_("Commission split percentages must total 100%. Current total: {0}%").format(
					total_percent
				)
			)


def auto_create_commission(doc, method):
	"""Hook: Auto-create Commission Record when Opportunity sales_stage becomes 'Closed Won'."""
	if doc.sales_stage != "Closed Won":
		return

	# Check if a Commission Record already exists for this Opportunity
	existing = frappe.db.exists("Commission Record", {"opportunity": doc.name})
	if existing:
		return

	# Create a new Commission Record in Draft
	commission = frappe.get_doc({
		"doctype": "Commission Record",
		"opportunity": doc.name,
		"deal_value": doc.opportunity_amount or 0,
		"commission_percent": 5,  # default 5% — can be changed
		"status": "Draft",
		"splits": [
			{
				"agent": doc.opportunity_owner or frappe.session.user,
				"split_percent": 100,
			}
		],
	})
	commission.insert(ignore_permissions=True)
	frappe.msgprint(
		_("Commission Record {0} created automatically.").format(commission.name),
		alert=True,
	)
