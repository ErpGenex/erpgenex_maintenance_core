# Copyright (c) 2026, ErpGenEx

"""MTBF/MTTR rollups by ISO 14224-style failure class (GAP-MNT-04)."""

from __future__ import annotations

from collections import defaultdict

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt, get_datetime


def _avg_hours_between(sorted_times: list) -> float | None:
	if len(sorted_times) < 2:
		return None
	total = 0.0
	for i in range(1, len(sorted_times)):
		total += (get_datetime(sorted_times[i]) - get_datetime(sorted_times[i - 1])).total_seconds()
	return round(total / (len(sorted_times) - 1) / 3600.0, 3)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	params: dict = {"company": filters.company}
	where = ["cwo.company = %(company)s", "cwo.docstatus = 1"]
	if filters.get("branch"):
		where.append("cwo.branch = %(branch)s")
		params["branch"] = filters.branch
	if filters.get("from_date"):
		where.append("DATE(COALESCE(cwo.failure_datetime, cwo.modified)) >= %(from_date)s")
		params["from_date"] = filters.from_date
	if filters.get("to_date"):
		where.append("DATE(COALESCE(cwo.failure_datetime, cwo.modified)) <= %(to_date)s")
		params["to_date"] = filters.to_date

	sql = f"""
		SELECT
			IFNULL(cwo.failure_class, '') AS failure_class,
			COUNT(*) AS submitted_wos,
			SUM(CASE WHEN cwo.asset_down = 1 THEN 1 ELSE 0 END) AS down_events,
			AVG(CASE WHEN cwo.asset_down = 1 AND cwo.downtime_hours IS NOT NULL
				THEN cwo.downtime_hours END) AS avg_mttr_hours
		FROM `tabCore Work Order` cwo
		WHERE {" AND ".join(where)}
		GROUP BY IFNULL(cwo.failure_class, '')
		ORDER BY submitted_wos DESC
	"""
	agg = frappe.db.sql(sql, params, as_dict=True)

	fail_rows = frappe.db.sql(
		f"""
		SELECT IFNULL(cwo.failure_class, '') AS failure_class, cwo.failure_datetime
		FROM `tabCore Work Order` cwo
		WHERE {" AND ".join(where)} AND cwo.asset_down = 1 AND cwo.failure_datetime IS NOT NULL
		ORDER BY failure_class, cwo.failure_datetime
		""",
		params,
		as_dict=True,
	)
	by_class: dict[str, list] = defaultdict(list)
	for r in fail_rows:
		by_class[r.failure_class].append(r.failure_datetime)

	for row in agg:
		row["avg_mttr_hours"] = flt(row.avg_mttr_hours, 3) if row.avg_mttr_hours is not None else None
		row["approx_mtbf_hours"] = _avg_hours_between(by_class.get(row.failure_class, []))

	columns = [
		{"label": _("Failure Class"), "fieldname": "failure_class", "fieldtype": "Link", "options": "Core Classification Code", "width": 160},
		{"label": _("Submitted WOs"), "fieldname": "submitted_wos", "fieldtype": "Int", "width": 110},
		{"label": _("Down Events"), "fieldname": "down_events", "fieldtype": "Int", "width": 100},
		{"label": _("Avg MTTR (h)"), "fieldname": "avg_mttr_hours", "fieldtype": "Float", "width": 110},
		{"label": _("Approx MTBF (h)"), "fieldname": "approx_mtbf_hours", "fieldtype": "Float", "width": 120},
	]

	return columns, agg
