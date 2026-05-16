# Copyright (c) 2026, ErpGenEx and contributors
# MIT License — see LICENSE

import frappe
from frappe.utils import add_days, flt, today
from frappe.utils.data import strip_html


def run_daily_pm_generators():
	"""Calendar PM + meter PM (IBM Maximo-style); single DB commit."""
	generate_pm_work_orders_calendar()
	generate_pm_work_orders_meter()
	frappe.db.commit()


def generate_pm_work_orders_calendar():
	"""Time-based preventive when Next Due Date is reached."""
	schedules = frappe.get_all(
		"Core PM Schedule",
		filters={
			"is_active": 1,
			"frequency_type": ["in", ["Time-Based", "Time And Meter"]],
			"next_due_date": ["<=", today()],
			"interval_days": [">", 0],
		},
		fields=[
			"name",
			"company",
			"branch",
			"subject_doctype",
			"subject_name",
			"default_work_order_type",
			"priority",
			"job_instructions",
			"interval_days",
		],
	)

	for sch in schedules:
		if not sch.get("subject_doctype") or not sch.get("subject_name"):
			continue

		_insert_pm_work_order(sch)

		frappe.db.set_value(
			"Core PM Schedule",
			sch.name,
			{"last_generated_date": today(), "next_due_date": add_days(today(), sch.interval_days)},
		)


def generate_pm_work_orders_meter():
	"""Meter-based PM using omnexa_fixed_assets Asset Meter Reading."""
	if not frappe.db.exists("DocType", "Asset Meter Reading"):
		return

	schedules = frappe.get_all(
		"Core PM Schedule",
		filters={
			"is_active": 1,
			"frequency_type": ["in", ["Meter-Based", "Time And Meter"]],
			"subject_doctype": "Fixed Asset",
		},
		fields=[
			"name",
			"company",
			"branch",
			"subject_doctype",
			"subject_name",
			"asset_meter_type",
			"meter_interval",
			"last_meter_reading",
			"default_work_order_type",
			"priority",
			"job_instructions",
		],
	)

	for sch in schedules:
		subject = sch.get("subject_name")
		meter_type = sch.get("asset_meter_type")
		if not subject or not meter_type or flt(sch.get("meter_interval")) <= 0:
			continue

		latest = frappe.db.sql(
			"""
			select value from `tabAsset Meter Reading`
			where asset = %s and meter_type = %s
			order by reading_time desc
			limit 1
			""",
			(subject, meter_type),
		)
		if not latest:
			continue

		latest_val = flt(latest[0][0])
		baseline = sch.get("last_meter_reading")

		if baseline is None:
			frappe.db.set_value("Core PM Schedule", sch.name, "last_meter_reading", latest_val)
			continue

		baseline_val = flt(baseline)
		if latest_val - baseline_val >= flt(sch.get("meter_interval")):
			_insert_pm_work_order(sch)
			frappe.db.set_value(
				"Core PM Schedule",
				sch.name,
				{"last_meter_reading": latest_val, "last_generated_date": today()},
			)


def _insert_pm_work_order(sch):
	doc = frappe.get_doc(
		{
			"doctype": "Core Work Order",
			"company": sch.get("company"),
			"branch": sch.get("branch"),
			"pm_schedule": sch.get("name"),
			"work_order_type": sch.get("default_work_order_type") or "Preventive",
			"priority": sch.get("priority") or "Medium",
			"subject_doctype": sch.get("subject_doctype"),
			"subject_name": sch.get("subject_name"),
			"description": strip_html(sch.get("job_instructions") or "")[:280],
			"status": "Draft",
		}
	)
	doc.insert(ignore_permissions=True)
