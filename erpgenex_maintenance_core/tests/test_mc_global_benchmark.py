# Copyright (c) 2026, Omnexa
import json, frappe
from frappe.tests.utils import FrappeTestCase
from erpgenex_maintenance_core.mc_gap_register import GLOBAL_LEADER_TARGET, get_gap_status
from erpgenex_maintenance_core.mc_global_benchmark import get_global_mc_score
from erpgenex_maintenance_core.workspace.mc_workspace import sync_mc_workspace_menu

class TestMcGlobalBenchmark(FrappeTestCase):
	def test_global_score(self):
		s = get_global_mc_score()
		self.assertGreaterEqual(s["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(s.get("global_leader_gate"))
	def test_gaps_closed(self):
		self.assertTrue(get_gap_status()["global_leader_gate"])
	def test_workspace_sync(self):
		stats = sync_mc_workspace_menu(save=True, rebuild=True)
		self.assertGreater(stats["total_links"], 10)
		ws = frappe.get_doc("Workspace", "Maintenance Core")
		self.assertGreater(len(ws.shortcuts), 5)
