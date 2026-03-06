app_name = "iybots_re_ops"
app_title = "Iybots Real Estate Ops"
app_publisher = "Iybots"
app_description = "Real Estate Operations System for Nigerian Companies"
app_email = "info@iybots.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "iybots_re_ops",
# 		"logo": "/assets/iybots_re_ops/logo.png",
# 		"title": "Iybots Real Estate Ops",
# 		"route": "/iybots_re_ops",
# 		"has_permission": "iybots_re_ops.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/iybots_re_ops/css/iybots_theme.css",
	"/assets/iybots_re_ops/css/dashboard.css",
]
app_include_js = "/assets/iybots_re_ops/js/dashboard_components.js"

# include js, css files in header of web template
web_include_css = "/assets/iybots_re_ops/css/portal.css"
# web_include_js = "/assets/iybots_re_ops/js/iybots_re_ops.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "iybots_re_ops/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "iybots_re_ops/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
	"Client Portal User": "portal"
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "iybots_re_ops.utils.jinja_methods",
# 	"filters": "iybots_re_ops.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "iybots_re_ops.install.before_install"
# after_install = "iybots_re_ops.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "iybots_re_ops.uninstall.before_uninstall"
# after_uninstall = "iybots_re_ops.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "iybots_re_ops.utils.before_app_install"
# after_app_install = "iybots_re_ops.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "iybots_re_ops.utils.before_app_uninstall"
# after_app_uninstall = "iybots_re_ops.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "iybots_re_ops.notifications.get_notification_config"

# Permissions
# -----------
# Row-level security: RE Agent sees only their own records.
# Uses lead_owner (Lead), opportunity_owner (Opportunity), agent (Commission Record, Agent Check-in).

_perm = "iybots_re_ops.iybots_real_estate_ops.permissions"

permission_query_conditions = {
	"Lead":              f"{_perm}.get_permission_query_conditions_for_lead",
	"Opportunity":       f"{_perm}.get_permission_query_conditions_for_opportunity",
	"Commission Record": f"{_perm}.get_permission_query_conditions_for_commission_record",
	"Agent Check-in":    f"{_perm}.get_permission_query_conditions_for_agent_check_in",
}

has_permission = {
	"Lead":              f"{_perm}.has_permission_for_lead",
	"Opportunity":       f"{_perm}.has_permission_for_opportunity",
	"Commission Record": f"{_perm}.has_permission_for_commission_record",
	"Agent Check-in":    f"{_perm}.has_permission_for_agent_check_in",
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

_crm = "iybots_re_ops.iybots_real_estate_ops.crm_hooks"
_comm = "iybots_re_ops.iybots_real_estate_ops.doctype.commission_record.commission_record"

doc_events = {
	"Opportunity": {
		"before_insert": f"{_crm}.opportunity_before_insert",
		"on_update": [
			f"{_crm}.opportunity_on_closed_won",
			f"{_comm}.auto_create_commission",
		],
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"iybots_re_ops.iybots_real_estate_ops.doctype.payment_plan.payment_plan.mark_overdue_milestones"
	]
}

# Testing
# -------

# before_tests = "iybots_re_ops.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "iybots_re_ops.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "iybots_re_ops.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["iybots_re_ops.utils.before_request"]
# after_request = ["iybots_re_ops.utils.after_request"]

# Job Events
# ----------
# before_job = ["iybots_re_ops.utils.before_job"]
# after_job = ["iybots_re_ops.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"iybots_re_ops.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["MD", "RE Admin", "RE Agent", "HR", "Client Portal User"]]]},
    {"dt": "Custom Field", "filters": [["module", "=", "Iybots Real Estate Ops"]]},
    {"dt": "Property Type", "filters": [["module", "=", "Iybots Real Estate Ops"]]},
    {"dt": "Sales Stage", "filters": [["name", "in", ["Inquiry", "Site Visit", "Offer", "Payment Plan", "Closed Won", "Closed Lost"]]]},
    {"dt": "Lead Source", "filters": [["name", "in", ["Instagram", "Property Show", "Referral - Agent", "Website", "Walk-in", "WhatsApp"]]]},
    {"dt": "Workspace", "filters": [["module", "=", "Iybots Real Estate Ops"]]},
    {"dt": "Number Card", "filters": [["module", "=", "Iybots Real Estate Ops"]]},
    {"dt": "Page", "filters": [["module", "=", "Iybots Real Estate Ops"]]},
]

website_context = {
    "favicon": "/assets/iybots_re_ops/images/favicon.ico",
    "splash_image": "/assets/iybots_re_ops/images/logo.png",
    "brand_html": "<div><img src='/assets/iybots_re_ops/images/logo.png' style='max-width:30px; margin-right:5px;'> Iybots Real Estate Ops</div>",
}
