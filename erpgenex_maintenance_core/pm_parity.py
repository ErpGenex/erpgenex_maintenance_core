# Copyright (c) 2026, ErpGenEx
import frappe


def preview_wo_backlog(company: str) -> dict:
	if not company:
		return {"open_csr": 0, "open_wo": 0}
	open_csr = frappe.db.count("Core Service Request", {"company": company, "status": ("in", ("Open", "In Progress"))})
	open_wo = frappe.db.count(
		"Core Work Order",
		{"company": company, "status": ("in", ("Draft", "Open", "In Progress"))},
	)
	return {
		"company": company,
		"open_service_requests": open_csr,
		"open_work_orders": open_wo,
		"backlog_total": open_csr + open_wo,
		"sap_module": "PM",
	}
