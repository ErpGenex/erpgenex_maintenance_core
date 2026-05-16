import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CoreSLAProfile(Document):
	def validate(self):
		for fld, lbl in (
			("response_hours", _("Target Response (hours)")),
			("resolution_hours", _("Target Resolution (hours)")),
		):
			val = getattr(self, fld, None)
			if val is None:
				continue
			if flt(val) < 0:
				frappe.throw(_("{0} cannot be negative.").format(lbl), title=_("SLA"))
