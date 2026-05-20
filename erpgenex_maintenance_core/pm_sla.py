# Copyright (c) 2026, ErpGenEx
"""SAP PM — SLA response/resolution helpers (pure functions + DB lookup)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import frappe
from frappe.utils import flt, get_datetime, now_datetime

DEFAULT_RESPONSE_HOURS = {
	"Critical": 2.0,
	"High": 8.0,
	"Medium": 24.0,
	"Low": 72.0,
}


def target_response_hours(priority: str, sla_profile: str | None = None) -> float:
	if sla_profile and frappe.db.exists("Core SLA Profile", sla_profile):
		hours = frappe.db.get_value("Core SLA Profile", sla_profile, "response_hours")
		if hours:
			return flt(hours)
	return DEFAULT_RESPONSE_HOURS.get((priority or "Medium").strip(), 24.0)


def is_sla_breached(
	opened_at: datetime,
	priority: str = "Medium",
	*,
	sla_profile: str | None = None,
	closed_at: datetime | None = None,
) -> dict[str, Any]:
	"""Return breach flag and hours elapsed vs target (SAP PM SLA KPI)."""
	opened = get_datetime(opened_at)
	closed = get_datetime(closed_at) if closed_at else now_datetime()
	elapsed_h = (closed - opened).total_seconds() / 3600.0
	target_h = target_response_hours(priority, sla_profile)
	return {
		"breached": elapsed_h > target_h,
		"elapsed_hours": round(elapsed_h, 3),
		"target_response_hours": target_h,
		"priority": priority,
	}
