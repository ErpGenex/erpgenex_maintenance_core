import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CorePMSchedule(Document):
	def validate(self):
		if self.subject_doctype and not self.subject_name:
			frappe.throw(_("Set Subject when Subject DocType is selected."))
		if self.subject_name and not self.subject_doctype:
			frappe.throw(_("Set Subject DocType when Subject is selected."))

		if self.frequency_type in ("Time-Based", "Time And Meter"):
			if not self.interval_days:
				frappe.throw(_("Interval (days) is required for time-based PM."))

		if self.frequency_type in ("Meter-Based", "Time And Meter"):
			if self.subject_doctype != "Fixed Asset":
				frappe.throw(
					_("Meter PM requires Subject DocType «Fixed Asset» (linked to Asset Meter Reading).")
				)
			if not self.asset_meter_type:
				frappe.throw(_("Select Meter Type for meter-based PM."))
			if flt(self.meter_interval) <= 0:
				frappe.throw(_("Meter Interval must be greater than zero."))
