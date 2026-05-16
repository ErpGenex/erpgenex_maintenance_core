"""Submitted Core Work Order KPIs per Fixed Asset subject (ISO 55000-oriented reliability hints).

MTTR uses downtime_hours where captured; approximate MTBF uses mean hours between successive
failure_datetime stamps on the same asset (failure-start spacing — not full operational calendar MTBF).
"""

from __future__ import annotations

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import get_datetime


FIXED_ASSET = "Fixed Asset"


def _avg_hours_between_failure_starts(sorted_times: list) -> float | None:
	if len(sorted_times) < 2:
		return None
	total_seconds = 0.0
	for i in range(1, len(sorted_times)):
		a = get_datetime(sorted_times[i])
		b = get_datetime(sorted_times[i - 1])
		total_seconds += (a - b).total_seconds()
	return round(total_seconds / (len(sorted_times) - 1) / 3600.0, 3)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	params: dict = {"company": filters.company, "fa_dt": FIXED_ASSET}
	base_where = [
		"cwo.company = %(company)s",
		"cwo.docstatus = 1",
		"cwo.subject_doctype = %(fa_dt)s",
		"cwo.subject_name IS NOT NULL",
		"cwo.subject_name != ''",
	]
	if filters.get("branch"):
		base_where.append("cwo.branch = %(branch)s")
		params["branch"] = filters.branch

	sample_where = list(base_where)
	if filters.get("from_date"):
		sample_where.append(
			"DATE(COALESCE(cwo.failure_datetime, cwo.completion_date, cwo.modified)) >= %(from_date)s"
		)
		params["from_date"] = filters.from_date
	if filters.get("to_date"):
		sample_where.append(
			"DATE(COALESCE(cwo.failure_datetime, cwo.completion_date, cwo.modified)) <= %(to_date)s"
		)
		params["to_date"] = filters.to_date

	where_sql = " AND ".join(sample_where)

	agg_rows = frappe.db.sql(
		f"""
		SELECT
			cwo.subject_name AS asset,
			COUNT(*) AS submitted_wos,
			SUM(CASE WHEN cwo.asset_down = 1 THEN 1 ELSE 0 END) AS asset_down_events,
			SUM(
				CASE WHEN cwo.asset_down = 1 AND cwo.downtime_hours IS NOT NULL THEN 1 ELSE 0 END
			) AS downtime_completed,
			AVG(
				CASE WHEN cwo.asset_down = 1 AND cwo.downtime_hours IS NOT NULL
					THEN cwo.downtime_hours END
			) AS avg_mttr_hours
		FROM `tabCore Work Order` cwo
		WHERE {where_sql}
		GROUP BY cwo.subject_name
		ORDER BY cwo.subject_name
		""",
		params,
		as_dict=True,
	)

	fail_where = list(base_where)
	fail_where.extend(["cwo.asset_down = 1", "cwo.failure_datetime IS NOT NULL"])
	fail_params = dict(params)
	if filters.get("from_date"):
		fail_where.append("DATE(cwo.failure_datetime) >= %(fail_from)s")
		fail_params["fail_from"] = filters.from_date
	if filters.get("to_date"):
		fail_where.append("DATE(cwo.failure_datetime) <= %(fail_to)s")
		fail_params["fail_to"] = filters.to_date

	fail_sql = " AND ".join(fail_where)
	fail_rows = frappe.db.sql(
		f"""
		SELECT cwo.subject_name AS asset, cwo.failure_datetime AS failure_datetime
		FROM `tabCore Work Order` cwo
		WHERE {fail_sql}
		ORDER BY cwo.subject_name, cwo.failure_datetime
		""",
		fail_params,
		as_dict=True,
	)

	by_asset_times: dict[str, list] = defaultdict(list)
	for row in fail_rows:
		by_asset_times[row.asset].append(row.failure_datetime)

	name_lookup = {}
	if agg_rows:
		asset_names = [r.asset for r in agg_rows]
		names = frappe.get_all(
			"Fixed Asset",
			filters={"name": ["in", asset_names]},
			fields=["name", "asset_name"],
		)
		name_lookup = {a.name: a.asset_name for a in names}

	for row in agg_rows:
		row["asset_name"] = name_lookup.get(row.asset, "")
		row["approx_mtbf_hours"] = _avg_hours_between_failure_starts(by_asset_times.get(row.asset, []))
		row["avg_mttr_hours"] = round(row.avg_mttr_hours, 3) if row.avg_mttr_hours is not None else None

	columns = [
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
	]

	return columns, agg_rows
