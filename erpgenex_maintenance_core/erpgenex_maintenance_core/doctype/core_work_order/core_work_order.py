import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from erpgenex_maintenance_core.coherence import validate_real_estate_unit_links


_EXPECTED_TAXONOMY = {
	"failure_class": "Failure Class",
	"failure_mode": "Failure Mode",
	"problem_code": "Problem",
	"cause_code": "Cause",
	"remedy_code": "Remedy",
}


class CoreWorkOrder(Document):
	def validate(self):
		validate_real_estate_unit_links(self)
		if self.subject_doctype and not self.subject_name:
			frappe.throw(_("Set Subject when Subject DocType is selected."))
		if self.subject_name and not self.subject_doctype:
			frappe.throw(_("Set Subject DocType when Subject is selected."))

		if self._will_issue_stock_on_submit() and not self.branch:
			frappe.throw(_("Branch is required when issuing stocked materials from a warehouse."))

		if getattr(self, "cost_center", None):
			cc_company = frappe.db.get_value("Cost Center", self.cost_center, "company")
			if cc_company and cc_company != self.company:
				frappe.throw(_("Cost Center belongs to a different company."), title=_("Company"))

		for fieldname, tax in _EXPECTED_TAXONOMY.items():
			code = self.get(fieldname)
			if not code:
				continue
			row_tax = frappe.db.get_value("Core Classification Code", code, "taxonomy")
			if row_tax != tax:
				frappe.throw(
					_("{0} must reference a Classification Code with taxonomy «{1}» (got «{2}»).").format(
						frappe.unscrub(fieldname).replace("_", " "), tax, row_tax or "?"
					)
				)

		total_labor = 0.0
		for row in self.get("labor_actuals") or []:
			row.labor_cost = flt(row.actual_hours) * flt(row.labor_rate)
			total_labor += flt(row.labor_cost)

		total_material = 0.0
		for row in self.get("material_actuals") or []:
			if row.get("stock_item"):
				row_vals = frappe.db.get_value(
					"Item", row.stock_item, ["item_code", "item_name", "stock_uom"]
				)
				if row_vals:
					it_code, it_name, it_uom = row_vals
					if it_code and not row.get("item_code"):
						row.item_code = it_code
					if it_name and not (row.get("item_description") or "").strip():
						row.item_description = it_name
					if it_uom and not (row.get("uom") or "").strip():
						row.uom = it_uom

			row.material_cost = flt(row.actual_qty) * flt(row.rate)
			total_material += flt(row.material_cost)

		self.actual_cost = flt(total_labor + total_material)

		self._compute_downtime()

	def _will_issue_stock_on_submit(self) -> bool:
		if not getattr(self, "issue_warehouse", None):
			return False
		for row in self.get("material_actuals") or []:
			if not row.get("stock_item") or flt(row.actual_qty) <= 0:
				continue
			if frappe.db.get_value("Item", row.stock_item, "is_stock_item"):
				return True
		return False

	def _compute_downtime(self):
		if (
			self.asset_down
			and self.failure_datetime
			and self.functional_restore_datetime
			and self.functional_restore_datetime >= self.failure_datetime
		):
			delta = frappe.utils.get_datetime(self.functional_restore_datetime) - frappe.utils.get_datetime(
				self.failure_datetime
			)
			self.downtime_hours = round(delta.total_seconds() / 3600.0, 3)
		elif self.asset_down and self.failure_datetime and not self.functional_restore_datetime:
			self.downtime_hours = None
		else:
			self.downtime_hours = None

	def on_submit(self):
		from erpgenex_maintenance_core.utils.stock_issue import create_stock_issue_for_core_work_order

		create_stock_issue_for_core_work_order(self)

	def on_cancel(self):
		from erpgenex_maintenance_core.utils.stock_issue import cancel_linked_stock_issue

		cancel_linked_stock_issue(self.name)
		self.db_set("status", "Cancelled", update_modified=False)
