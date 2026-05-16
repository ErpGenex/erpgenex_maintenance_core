"""Create omnexa_accounting Stock Entry (Material Issue) from Core Work Order material lines."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def posting_reference(work_order_name: str) -> str:
	return f"Core Work Order:{work_order_name}"


def create_stock_issue_for_core_work_order(doc) -> str | None:
	"""Submit a Material Issue Stock Entry linked via ``reference``. Updates ``maintenance_stock_entry``."""
	if not frappe.db.exists("DocType", "Stock Entry"):
		return None

	warehouse = getattr(doc, "issue_warehouse", None)
	if not warehouse:
		return None

	reference = posting_reference(doc.name)
	se_meta = frappe.get_meta("Stock Entry")
	filters = {"company": doc.company, "reference": reference}
	if getattr(doc, "branch", None) and se_meta.has_field("branch"):
		filters["branch"] = doc.branch

	existing = frappe.db.get_value("Stock Entry", filters, "name")
	if existing:
		doc.db_set("maintenance_stock_entry", existing, update_modified=False)
		return existing

	items: list[dict] = []
	for row in doc.get("material_actuals") or []:
		item_name = row.get("stock_item")
		if not item_name:
			continue
		qty = flt(row.actual_qty)
		if qty <= 0:
			continue
		if not frappe.db.get_value("Item", item_name, "is_stock_item"):
			continue

		items.append(
			{
				"item": item_name,
				"item_code": row.get("item_code"),
				"s_warehouse": warehouse,
				"qty": qty,
				"rate": flt(row.rate),
				"uom": row.get("uom"),
			}
		)

	if not items:
		return None

	posting_date = getdate(doc.completion_date) if doc.completion_date else getdate(today())

	se = frappe.new_doc("Stock Entry")
	se.company = doc.company
	if getattr(doc, "branch", None) and se_meta.has_field("branch"):
		se.branch = doc.branch
	if getattr(doc, "cost_center", None) and se_meta.has_field("cost_center"):
		se.cost_center = doc.cost_center
	se.purpose = "Material Issue"
	se.posting_date = posting_date
	se.reference = reference
	se.from_warehouse = warehouse
	se.remarks = _("Maintenance material issue for {0}").format(doc.name)
	se.items = items
	frappe.flags.ignore_permissions = True
	try:
		se.insert()
		se.submit()
	finally:
		frappe.flags.ignore_permissions = False

	doc.db_set("maintenance_stock_entry", se.name, update_modified=False)
	return se.name


def cancel_linked_stock_issue(work_order_name: str, stock_entry_name: str | None = None) -> None:
	if not stock_entry_name:
		stock_entry_name = frappe.db.get_value(
			"Core Work Order", work_order_name, "maintenance_stock_entry"
		)
	if not stock_entry_name:
		return

	se = frappe.get_doc("Stock Entry", stock_entry_name)
	if int(se.docstatus or 0) == 1:
		frappe.flags.ignore_permissions = True
		try:
			se.cancel()
		finally:
			frappe.flags.ignore_permissions = False

	frappe.db.set_value("Core Work Order", work_order_name, "maintenance_stock_entry", None)
