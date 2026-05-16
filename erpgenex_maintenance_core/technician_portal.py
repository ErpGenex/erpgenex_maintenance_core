# Copyright (c) 2026, ErpGenEx
# License: MIT

"""Field technician portal (GAP-MNT-03)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint


TECHNICIAN_ROLES = frozenset({"Maintenance Technician", "Maintenance Manager", "System Manager"})


def _assert_technician() -> str:
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Login required"), frappe.AuthenticationError)
	roles = set(frappe.get_roles(user))
	if not roles & TECHNICIAN_ROLES:
		frappe.throw(_("Maintenance Technician access required."), frappe.PermissionError)
	return user


@frappe.whitelist()
def portal_get_assigned_work_orders(limit_page_length: int | None = 20) -> list[dict]:
	"""Work orders assigned to the current technician."""
	user = _assert_technician()
	length = max(1, min(cint(limit_page_length, default=20), 100))
	filters: dict = {"assigned_to": user, "status": ["not in", ["Cancelled"]]}
	if "System Manager" in frappe.get_roles(user) or "Maintenance Manager" in frappe.get_roles(user):
		filters = {"status": ["not in", ["Cancelled"]]}
	return frappe.get_list(
		"Core Work Order",
		filters=filters,
		fields=[
			"name",
			"status",
			"priority",
			"company",
			"pmc_property_unit",
			"re_unit_inventory",
			"planned_start",
			"completion_date",
			"modified",
		],
		order_by="modified desc",
		limit_page_length=length,
	)


@frappe.whitelist()
def portal_update_work_order_status(work_order: str, status: str) -> dict:
	_assert_technician()
	allowed = {"Draft", "In Progress", "Completed", "On Hold"}
	if status not in allowed:
		frappe.throw(_("Status must be one of: {0}").format(", ".join(sorted(allowed))))
	doc = frappe.get_doc("Core Work Order", work_order)
	if doc.assigned_to and doc.assigned_to != frappe.session.user:
		if "Maintenance Manager" not in frappe.get_roles():
			frappe.throw(_("This work order is assigned to another technician."))
	doc.status = status
	doc.save(ignore_permissions=False)
	return {"name": doc.name, "status": doc.status}
