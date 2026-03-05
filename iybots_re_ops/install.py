# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, add_months

def after_migrate():
	"""Run after bench migrate"""
	pass


@frappe.whitelist()
def load_demo_data():
	"""Creates sample Nigerian real estate data for testing."""
	frappe.only_for("Administrator")

	create_sample_properties()
	create_sample_leads()
	create_sample_payment_plans()

	frappe.db.commit()
	return "Demo data loaded successfully."


def create_sample_properties():
	properties = [
		{"property_name": "Lekki Phase 1 Luxury Duplex", "property_type": "Duplex", "location": "Lekki Phase 1, Lagos", "price": 180000000, "status": "Available", "developer": "Iybots Homes", "description": "4-bedroom semi-detached duplex with BQ."},
		{"property_name": "Epe Smart City Plots", "property_type": "Land", "location": "Epe, Lagos", "price": 8500000, "status": "Available", "developer": "Iybots Homes", "description": "500sqm residential plots with C of O."},
		{"property_name": "Victoria Island Penthouse", "property_type": "Apartment", "location": "Victoria Island, Lagos", "price": 350000000, "status": "Available", "developer": "Luxury Build Ltd", "description": "3-bedroom luxury penthouse with ocean view."},
		{"property_name": "Ikoyi Commercial Plaza Space", "property_type": "Commercial", "location": "Ikoyi, Lagos", "price": 25000000, "status": "Available", "developer": "Iybots Homes", "description": "Open plan office space in premium location."},
		{"property_name": "Ajah Family Bungalow", "property_type": "Duplex", "location": "Ajah, Lagos", "price": 45000000, "status": "Sold", "developer": "Iybots Homes", "description": "3-bedroom fully detached bungalow."}
	]

	for p in properties:
		if not frappe.db.exists("Property", {"property_name": p["property_name"]}):
			doc = frappe.get_doc({
				"doctype": "Property",
				**p
			})
			doc.insert(ignore_permissions=True)


def create_sample_leads():
	leads = [
		{"first_name": "Chukwuemeka", "last_name": "Obi", "email_id": "c.obi@example.com", "mobile_no": "08012345678", "budget_min": 100000000, "budget_max": 200000000, "preferred_location": "Lekki or Ikoyi", "property_type_interest": "Duplex", "diaspora_flag": 0, "financing_method": "Mortgage", "urgency": "Hot", "status": "Lead"},
		{"first_name": "Aisha", "last_name": "Mohammed", "email_id": "a.mohammed@example.com", "mobile_no": "08087654321", "budget_min": 5000000, "budget_max": 15000000, "preferred_location": "Epe", "property_type_interest": "Land", "diaspora_flag": 1, "financing_method": "Installment", "urgency": "Warm", "status": "Opportunity"},
		{"first_name": "Oluwaseun", "last_name": "Adeyemi", "email_id": "seun.a@example.com", "mobile_no": "08123456789", "budget_min": 50000000, "budget_max": 80000000, "preferred_location": "Ajah", "property_type_interest": "Apartment", "diaspora_flag": 0, "financing_method": "Cash", "urgency": "Cold", "status": "Open"}
	]

	for l in leads:
		if not frappe.db.exists("Lead", {"email_id": l["email_id"]}):
			doc = frappe.get_doc({
				"doctype": "Lead",
				**l
			})
			try:
				doc.insert(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Failed to create demo lead {l['email_id']}: {str(e)}")


def create_sample_payment_plans():
	# get customer
	customer = frappe.db.get_value("Customer", {"customer_name": ["like", "%"]}, "name")
	property_name = frappe.db.get_value("Property", {"status": "Available"}, "name")
	
	if not customer or not property_name:
		return

	if not frappe.db.exists("Payment Plan", {"plan_title": "Demo Epe Land Plan"}):
		doc = frappe.get_doc({
			"doctype": "Payment Plan",
			"plan_title": "Demo Epe Land Plan",
			"customer": customer,
			"property": property_name,
			"total_amount": 8500000,
			"status": "Active",
			"milestones": [
				{"due_date": add_months(today(), -1), "amount": 2500000, "status": "Paid", "payment_ref": "GTB/TRF/001"},
				{"due_date": add_days(today(), -2), "amount": 2000000, "status": "Pending", "notes": "Should be overdue"},
				{"due_date": add_days(today(), 3), "amount": 2000000, "status": "Pending", "notes": "Due this week"},
				{"due_date": add_months(today(), 1), "amount": 2000000, "status": "Pending"}
			]
		})
		try:
			doc.insert(ignore_permissions=True)
			# run calculate totals
			doc.calculate_totals()
			doc.db_update()
		except Exception as e:
			frappe.log_error(f"Failed to create demo payment plan: {str(e)}")
