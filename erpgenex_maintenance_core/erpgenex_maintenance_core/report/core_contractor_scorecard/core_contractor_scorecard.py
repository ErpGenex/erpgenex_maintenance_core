from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	params: dict = {"company": filters.company}
	where = ["cwo.company = %(company)s", "cwo.docstatus = 1"]
	if filters.get("from_date"):
		where.append("DATE(cwo.modified) >= %(from_date)s")
		params["from_date"] = filters.from_date
	if filters.get("to_date"):
		where.append("DATE(cwo.modified) <= %(to_date)s")
		params["to_date"] = filters.to_date

	# Use assigned_to user as proxy when supplier not on WO; labor lines may reference supplier in future.
	rows = frappe.db.sql(
		f"""
		SELECT
			IFNULL(cwo.assigned_to, 'Unassigned') AS contractor_key,
			COUNT(*) AS work_orders,
			AVG(cwo.actual_cost) AS avg_cost,
			AVG(cwo.downtime_hours) AS avg_downtime_hours,
			SUM(CASE WHEN cwo.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count
		FROM `tabCore Work Order` cwo
		WHERE {" AND ".join(where)}
		GROUP BY IFNULL(cwo.assigned_to, 'Unassigned')
		ORDER BY work_orders DESC
		""",
		params,
		as_dict=True,
	)
	for r in rows:
		r["completion_rate"] = round(100.0 * flt(r.completed_count) / max(1, r.work_orders), 2)
		r["avg_cost"] = flt(r.avg_cost, 2) if r.avg_cost is not None else None
		r["avg_downtime_hours"] = flt(r.avg_downtime_hours, 2) if r.avg_downtime_hours is not None else None

	columns = [
		{"label": _("Contractor / Assignee"), "fieldname": "contractor_key", "fieldtype": "Data", "width": 160},
		{"label": _("Work Orders"), "fieldname": "work_orders", "fieldtype": "Int", "width": 100},
		{"label": _("Completed"), "fieldname": "completed_count", "fieldtype": "Int", "width": 90},
		{"label": _("Completion %"), "fieldname": "completion_rate", "fieldtype": "Percent", "width": 100},
		{"label": _("Avg Cost"), "fieldname": "avg_cost", "fieldtype": "Currency", "width": 100},
		{"label": _("Avg Downtime (h)"), "fieldname": "avg_downtime_hours", "fieldtype": "Float", "width": 110},
	]
	return columns, rows
