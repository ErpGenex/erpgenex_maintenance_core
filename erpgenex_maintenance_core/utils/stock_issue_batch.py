# Copyright (c) 2026, ErpGenEx
# License: MIT

"""Consolidated material issue across work orders (GAP-MNT-05)."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import flt, getdate, today

from erpgenex_maintenance_core.utils.stock_issue import posting_reference


@frappe.whitelist()
def issue_materials_batch(work_orders: str | list, warehouse: str | None = None) -> dict:
	"""Create one Stock Entry for stocked material lines on multiple submitted/draft WOs."""
	frappe.has_permission("Core Work Order", "write", throw=True)
	if isinstance(work_orders, str):
		work_orders = json.loads(work_orders) if work_orders.strip().startswith("[") else [work_orders]
	if not work_orders:
		frappe.throw(_("Select at least one work order."))

	if not frappe.db.exists("DocType", "Stock Entry"):
		frappe.throw(_("Stock Entry is not available on this site."))

	company = None
	branch = None
	items: list[dict] = []
	references: list[str] = []

	for wo_name in work_orders:
		doc = frappe.get_doc("Core Work Order", wo_name)
		company = company or doc.company
		if doc.company != company:
			frappe.throw(_("All work orders must belong to the same company."))
		branch = branch or getattr(doc, "branch", None)
		wh = warehouse or getattr(doc, "issue_warehouse", None)
		if not wh:
			frappe.throw(_("Set Issue Warehouse on {0} or pass warehouse.").format(wo_name))
		references.append(posting_reference(wo_name))
		for row in doc.get("material_actuals") or []:
			if not row.get("stock_item") or flt(row.actual_qty) <= 0:
				continue
			if not frappe.db.get_value("Item", row.stock_item, "is_stock_item"):
				continue
			items.append(
				{
					"item": row.stock_item,
					"item_code": row.get("item_code"),
					"s_warehouse": wh,
					"qty": flt(row.actual_qty),
					"rate": flt(row.rate),
					"uom": row.get("uom"),
				}
			)

	if not items:
		frappe.throw(_("No stocked material lines to issue."))

	ref_key = "Batch:" + ",".join(sorted(work_orders))
	se = frappe.new_doc("Stock Entry")
	se.company = company
	se_meta = frappe.get_meta("Stock Entry")
	if branch and se_meta.has_field("branch"):
		se.branch = branch
	se.purpose = "Material Issue"
	se.posting_date = getdate(today())
	se.reference = ref_key[:140]
	se.from_warehouse = warehouse or items[0]["s_warehouse"]
	se.remarks = _("Batch maintenance issue for {0}").format(", ".join(work_orders[:5]))
	se.items = items
	se.insert(ignore_permissions=True)
	se.submit()

	for wo_name in work_orders:
		frappe.db.set_value("Core Work Order", wo_name, "maintenance_stock_entry", se.name, update_modified=False)

	return {"stock_entry": se.name, "work_orders": work_orders, "item_count": len(items)}
