# Copyright (c) 2026, ErpGenEx
# License: MIT

from __future__ import annotations

import frappe
from frappe import _


def sync_real_estate_unit_links(doc) -> None:
	"""Keep explicit PMC/RE links aligned with premises dynamic link (GAP-MNT-01)."""
	if getattr(doc, "pmc_property_unit", None):
		doc.premises_doctype = "PMC Property Unit"
		doc.premises_name = doc.pmc_property_unit
	elif getattr(doc, "re_unit_inventory", None):
		doc.premises_doctype = "RE Unit Inventory"
		doc.premises_name = doc.re_unit_inventory


def validate_real_estate_unit_links(doc, expected_company: str | None = None) -> None:
	company = expected_company or getattr(doc, "company", None)
	if getattr(doc, "pmc_property_unit", None):
		_co = frappe.db.get_value("PMC Property Unit", doc.pmc_property_unit, "company")
		if company and _co and _co != company:
			frappe.throw(
				_("PMC Property Unit {0} belongs to company {1}.").format(
					frappe.bold(doc.pmc_property_unit), frappe.bold(_co)
				),
				title=_("Company mismatch"),
			)
	if getattr(doc, "re_unit_inventory", None):
		_co = frappe.db.get_value("RE Unit Inventory", doc.re_unit_inventory, "company")
		if company and _co and _co != company:
			frappe.throw(
				_("RE Unit Inventory {0} belongs to company {1}.").format(
					frappe.bold(doc.re_unit_inventory), frappe.bold(_co)
				),
				title=_("Company mismatch"),
			)
	sync_real_estate_unit_links(doc)
