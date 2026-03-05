# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class AgentCheckin(Document):
	def before_insert(self):
		self.validate_one_checkin_per_day()

	def validate_one_checkin_per_day(self):
		"""Ensure only one check-in per agent per day."""
		check_in_date = getdate(self.check_in_time) if self.check_in_time else getdate(nowdate())

		existing = frappe.db.exists(
			"Agent Check-in",
			{
				"agent": self.agent,
				"check_in_time": ["between", [
					f"{check_in_date} 00:00:00",
					f"{check_in_date} 23:59:59"
				]],
				"name": ["!=", self.name or ""],
			},
		)

		if existing:
			frappe.throw(
				_("Agent {0} has already checked in today. Only one check-in per day is allowed.").format(
					self.agent
				)
			)
