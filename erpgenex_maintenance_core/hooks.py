app_name = "erpgenex_maintenance_core"
app_title = "ERPGenEx Maintenance Core"
app_publisher = "ErpGenEx"
app_description = "Shared CMMS engine for fixed assets, property, rental, and facilities."
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core", "omnexa_accounting"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "erpgenex_maintenance_core",
# 		"logo": "/assets/erpgenex_maintenance_core/logo.png",
# 		"title": "ERPGenEx Maintenance Core",
# 		"route": "/erpgenex_maintenance_core",
# 		"has_permission": "erpgenex_maintenance_core.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpgenex_maintenance_core/css/erpgenex_maintenance_core.css"
# app_include_js = "/assets/erpgenex_maintenance_core/js/erpgenex_maintenance_core.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpgenex_maintenance_core/css/erpgenex_maintenance_core.css"
# web_include_js = "/assets/erpgenex_maintenance_core/js/erpgenex_maintenance_core.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpgenex_maintenance_core/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Core Service Request": "public/js/core_service_request.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erpgenex_maintenance_core/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpgenex_maintenance_core.utils.jinja_methods",
# 	"filters": "erpgenex_maintenance_core.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpgenex_maintenance_core.install.before_install"
# after_install = "erpgenex_maintenance_core.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "erpgenex_maintenance_core.uninstall.before_uninstall"
# after_uninstall = "erpgenex_maintenance_core.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erpgenex_maintenance_core.utils.before_app_install"
# after_app_install = "erpgenex_maintenance_core.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erpgenex_maintenance_core.utils.before_app_uninstall"
# after_app_uninstall = "erpgenex_maintenance_core.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpgenex_maintenance_core.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Core Service Request": "erpgenex_maintenance_core.permissions.get_core_service_request_query_conditions",
}

has_permission = {
	"Core Service Request": "erpgenex_maintenance_core.permissions.core_service_request_has_permission",
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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": ["erpgenex_maintenance_core.tasks.run_daily_pm_generators"],
}

# Testing
# -------

# before_tests = "erpgenex_maintenance_core.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpgenex_maintenance_core.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpgenex_maintenance_core.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erpgenex_maintenance_core.utils.before_request"]
# after_request = ["erpgenex_maintenance_core.utils.after_request"]

# Job Events
# ----------
# before_job = ["erpgenex_maintenance_core.utils.before_job"]
# after_job = ["erpgenex_maintenance_core.utils.after_job"]

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
# 	"erpgenex_maintenance_core.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["Maintenance Manager", "Maintenance Portal User", "Maintenance Technician"]]]},
]

