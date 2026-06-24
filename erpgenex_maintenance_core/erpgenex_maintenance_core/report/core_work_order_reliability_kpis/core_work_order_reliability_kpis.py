# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(filters, "Core Work Order", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Core Work Order",
		fields=['name', 'asset_name'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label": _("Asset"), "fieldname": "asset", "fieldtype": "Link", "options": "Fixed Asset", "width": 140},
		{"label": _("Asset Name"), "fieldname": "asset_name", "fieldtype": "Data", "width": 180},
		{"label": _("Submitted WOs"), "fieldname": "submitted_wos", "fieldtype": "Int", "width": 110},
		{"label": _("Asset Down Flags"), "fieldname": "asset_down_events", "fieldtype": "Int", "width": 130},
		{
			"label": _("Downtime Completed (#)"),
			"fieldname": "downtime_completed",
			"fieldtype": "Int",
			"width": 160,
		},
		{"label": _("Avg MTTR (h)"), "fieldname": "avg_mttr_hours", "fieldtype": "Float", "width": 110},
		{
			"label": _("Approx MTBF (h)"),
			"fieldname": "approx_mtbf_hours",
			"fieldtype": "Float",
			"width": 130,
		},
	], data
