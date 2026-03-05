// Copyright (c) 2026, Iybots and contributors
// For license information, please see license.txt

frappe.query_reports["Overdue Payments"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        }
    ]
};
