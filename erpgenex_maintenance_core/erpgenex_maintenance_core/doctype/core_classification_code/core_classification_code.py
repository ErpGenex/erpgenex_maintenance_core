from frappe.model.document import Document


class CoreClassificationCode(Document):
	def validate(self):
		self.code = (self.code or "").strip()
		self.title = (self.title or "").strip()
