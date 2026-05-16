import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CoreWOMaterialActual(Document):
	def validate(self):
		if getattr(self, "stock_item", None):
			row_vals = frappe.db.get_value(
				"Item", self.stock_item, ["item_code", "item_name", "stock_uom"]
			)
			if row_vals:
				it_code, it_name, it_uom = row_vals
				if it_code and not self.get("item_code"):
					self.item_code = it_code
				if it_name and not (self.get("item_description") or "").strip():
					self.item_description = it_name
				if it_uom and not (self.get("uom") or "").strip():
					self.uom = it_uom
		self.material_cost = flt(self.actual_qty) * flt(self.rate)
