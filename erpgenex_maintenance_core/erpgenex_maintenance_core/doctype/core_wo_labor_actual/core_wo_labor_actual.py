from frappe.model.document import Document
from frappe.utils import flt


class CoreWOLaborActual(Document):
	def validate(self):
		self.labor_cost = flt(self.actual_hours) * flt(self.labor_rate)
