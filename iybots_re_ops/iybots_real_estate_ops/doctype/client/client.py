# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Client(Document):
	def validate(self):
		if self.linked_user:
			self.ensure_portal_role()

	def ensure_portal_role(self):
		"""Ensure the linked user has the Client Portal User role."""
		user = frappe.get_doc("User", self.linked_user)
		role_names = [r.role for r in user.roles]
		if "Client Portal User" not in role_names:
			user.append("roles", {"role": "Client Portal User"})
			user.save(ignore_permissions=True)
