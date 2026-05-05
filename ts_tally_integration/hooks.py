app_name = "ts_tally_integration"
app_title = "Tally Integration"
app_publisher = "Siddarth"
app_description = "Integrate Tally With Erpnext"
app_email = "thirvusoft@gmail.com"
app_license = "mit"
required_apps = ["frappe/erpnext"]
# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "ts_tally_integration",
# 		"logo": "/assets/ts_tally_integration/logo.png",
# 		"title": "Tally Integration",
# 		"route": "/ts_tally_integration",
# 		"has_permission": "ts_tally_integration.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ts_tally_integration/css/ts_tally_integration.css"
# app_include_js = "/assets/ts_tally_integration/js/ts_tally_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/ts_tally_integration/css/ts_tally_integration.css"
# web_include_js = "/assets/ts_tally_integration/js/ts_tally_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ts_tally_integration/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Sales Invoice": "tally_integration/utils/js/sales_invoice.js",
	"Purchase Invoice": "tally_integration/utils/js/purchase_invoice.js",
	"Journal Entry": "tally_integration/utils/js/journal_entry.js",
	"Payment Entry": "tally_integration/utils/js/payment_entry.js",
}
doctype_list_js = {
	"Sales Invoice": "tally_integration/utils/js/sales_invoice_list.js",
	"Purchase Invoice": "tally_integration/utils/js/purchase_invoice_list.js",
	"Journal Entry": "tally_integration/utils/js/journal_entry_list.js",
	"Payment Entry": "tally_integration/utils/js/payment_entry_list.js",
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ts_tally_integration/public/icons.svg"

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
# 	"methods": "ts_tally_integration.utils.jinja_methods",
# 	"filters": "ts_tally_integration.utils.jinja_filters"
# }

# Installation
# ------------

after_migrate = "ts_tally_integration.tally_integration.utils.py.after_migrate.after_migrate"


# Uninstallation
# ------------

# before_uninstall = "ts_tally_integration.uninstall.before_uninstall"
# after_uninstall = "ts_tally_integration.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ts_tally_integration.utils.before_app_install"
# after_app_install = "ts_tally_integration.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ts_tally_integration.utils.before_app_uninstall"
# after_app_uninstall = "ts_tally_integration.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ts_tally_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"validate": "ts_tally_integration.tally_integration.utils.py.amended_from.validate",
	},
 	"Purchase Invoice": {
		"validate": "ts_tally_integration.tally_integration.utils.py.amended_from.validate",
	},
	"Journal Entry": {
		"validate": "ts_tally_integration.tally_integration.utils.py.amended_from.validate",
	},
 	"Payment Entry": {
		"validate": "ts_tally_integration.tally_integration.utils.py.amended_from.validate",
	},
 	"Stock Entry": {
		"validate": "ts_tally_integration.tally_integration.utils.py.amended_from.validate",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ts_tally_integration.tasks.all"
# 	],
# 	"daily": [
# 		"ts_tally_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"ts_tally_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ts_tally_integration.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ts_tally_integration.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ts_tally_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ts_tally_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ts_tally_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ts_tally_integration.utils.before_request"]
# after_request = ["ts_tally_integration.utils.after_request"]

# Job Events
# ----------
# before_job = ["ts_tally_integration.utils.before_job"]
# after_job = ["ts_tally_integration.utils.after_job"]

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
# 	"ts_tally_integration.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

