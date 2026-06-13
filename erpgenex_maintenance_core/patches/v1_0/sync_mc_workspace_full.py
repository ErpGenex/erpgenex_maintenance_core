# Copyright (c) 2026, Omnexa
import os
import frappe
from frappe.modules.import_file import import_file_by_path

def _ensure_pages():
	p = frappe.get_app_path("erpgenex_maintenance_core", "erpgenex_maintenance_core", "page")
	if not os.path.isdir(p):
		return
	for folder in os.listdir(p):
		jp = os.path.join(p, folder, f"{folder}.json")
		if os.path.isfile(jp):
			import_file_by_path(jp, force=True)

def execute():
	_ensure_pages()
	if frappe.db.exists("Workspace", "Maintenance Core"):
		from erpgenex_maintenance_core.workspace.mc_workspace import sync_mc_workspace_menu
		sync_mc_workspace_menu(save=True, rebuild=True)
