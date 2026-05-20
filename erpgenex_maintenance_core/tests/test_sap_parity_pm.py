# Copyright (c) 2026, ErpGenEx
from datetime import timedelta

from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

from erpgenex_maintenance_core.pm_sla import DEFAULT_RESPONSE_HOURS, is_sla_breached, target_response_hours


class TestSapParityPm(FrappeTestCase):
	def test_critical_default_hours(self):
		self.assertEqual(target_response_hours("Critical"), DEFAULT_RESPONSE_HOURS["Critical"])

	def test_sla_not_breached_when_recent(self):
		opened = now_datetime() - timedelta(hours=1)
		out = is_sla_breached(opened, priority="Critical")
		self.assertFalse(out["breached"])

	def test_sla_breached_when_old(self):
		opened = now_datetime() - timedelta(hours=48)
		out = is_sla_breached(opened, priority="Medium")
		self.assertTrue(out["breached"])

	def test_wo_backlog_preview_structure(self):
		import frappe

		from erpgenex_maintenance_core.pm_parity import preview_wo_backlog

		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company")
		out = preview_wo_backlog(company)
		self.assertIn("backlog_total", out)
