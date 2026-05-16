import frappe
from frappe import _
from frappe.model.document import Document

from erpgenex_maintenance_core.coherence import validate_real_estate_unit_links


class CoreServiceRequest(Document):
	def validate(self):
		validate_real_estate_unit_links(self)
		if self.subject_doctype and not self.subject_name:
			frappe.throw(_("Set Subject when Subject DocType is selected."))
		if self.subject_name and not self.subject_doctype:
			frappe.throw(_("Set Subject DocType when Subject is selected."))

		if self.premises_doctype and not self.premises_name:
			frappe.throw(_("Set Premises / Unit when Premises DocType is selected."))
		if self.premises_name and not self.premises_doctype:
			frappe.throw(_("Set Premises DocType when Premises / Unit is selected."))

	def before_insert(self):
		if not self.raised_by:
			self.raised_by = frappe.session.user
