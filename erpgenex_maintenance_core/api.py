import frappe
from frappe import _
from frappe.utils import cint
from frappe.utils.data import strip_html

_VALID_CSR_PRIORITY = frozenset({"Low", "Medium", "High", "Critical"})


def _ensure_optional_link(doctype: str | None, name: str | None, label: str) -> None:
	if not doctype and not name:
		return
	if bool(doctype) ^ bool(name):
		frappe.throw(_("{0}: set both DocType and document name or leave both empty.").format(label))
	if not frappe.db.exists("DocType", doctype):
		frappe.throw(_("Unknown DocType {0}").format(frappe.bold(doctype)))
	if not frappe.db.exists(doctype, name):
		frappe.throw(_("{0} {1} does not exist").format(doctype, frappe.bold(name)))


@frappe.whitelist()
def portal_create_service_request(
	company: str,
	description: str,
	priority: str = "Medium",
	branch: str | None = None,
	subject_doctype: str | None = None,
	subject_name: str | None = None,
	premises_doctype: str | None = None,
	premises_name: str | None = None,
) -> dict[str, str]:
	"""Create a Core Service Request for the logged-in tenant user (portal role).

	Intended for website/mobile clients using a **Maintenance Portal User** system login.
	Does not allow choosing SLA profile — FM assigns policy on triage.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Login required"), frappe.AuthenticationError)

	frappe.has_permission("Core Service Request", "create", throw=True)

	company = (company or "").strip()
	if not company or not frappe.db.exists("Company", company):
		frappe.throw(_("Valid Company is required"))

	priority = (priority or "Medium").strip()
	if priority not in _VALID_CSR_PRIORITY:
		frappe.throw(_("Priority must be one of: {0}").format(", ".join(sorted(_VALID_CSR_PRIORITY))))

	body = strip_html(description or "").strip()
	if not body:
		frappe.throw(_("Description is required"))

	_ensure_optional_link(subject_doctype, subject_name, _("Subject"))
	_ensure_optional_link(premises_doctype, premises_name, _("Premises / Unit"))

	doc = frappe.new_doc("Core Service Request")
	doc.company = company
	doc.branch = (branch or "").strip() or None
	doc.priority = priority
	doc.description = body[:65000]
	doc.status = "Open"
	doc.subject_doctype = subject_doctype
	doc.subject_name = subject_name
	doc.premises_doctype = premises_doctype
	doc.premises_name = premises_name
	doc.raised_by = user

	doc.insert(ignore_permissions=False)

	return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def portal_get_my_service_requests(limit_start: int | None = None, limit_page_length: int | None = None) -> list:
	"""Return Core Service Requests raised by the current user (respects DocPerm + portal row scope)."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Login required"), frappe.AuthenticationError)

	frappe.has_permission("Core Service Request", "read", throw=True)

	start = cint(limit_start, default=0)
	length = cint(limit_page_length, default=20)
	length = max(1, min(length, 100))

	return frappe.get_list(
		"Core Service Request",
		filters={"raised_by": frappe.session.user},
		fields=["name", "status", "priority", "company", "branch", "creation", "modified"],
		order_by="modified desc",
		limit_start=start,
		limit_page_length=length,
	)


@frappe.whitelist()
def preview_sla_status(
	priority: str = "Medium",
	sla_profile: str | None = None,
	opened_at: str | None = None,
) -> dict:
	"""SAP PM parity — SLA breach preview without mutating documents."""
	from frappe.utils import now_datetime

	from erpgenex_maintenance_core.pm_sla import is_sla_breached

	opened = opened_at or str(now_datetime())
	return is_sla_breached(opened, priority=priority, sla_profile=sla_profile)


@frappe.whitelist()
def preview_wo_backlog(company: str) -> dict:
	from erpgenex_maintenance_core.pm_parity import preview_wo_backlog as _preview

	return _preview(company)


@frappe.whitelist()
def make_core_work_order(service_request: str) -> str:
	"""Create a draft Core Work Order from a Core Service Request."""
	frappe.has_permission("Core Service Request", "read", doc=service_request, throw=True)
	frappe.has_permission("Core Work Order", "create", throw=True)

	source = frappe.get_doc("Core Service Request", service_request)

	wo = frappe.new_doc("Core Work Order")
	wo.naming_series = "CWO-.####"
	wo.company = source.company
	wo.branch = source.branch
	wo.service_request = source.name
	wo.status = "Draft"
	wo.work_order_type = "Corrective"
	wo.priority = source.priority or "Medium"
	if source.sla_profile:
		wo.sla_profile = source.sla_profile
	if source.assigned_to:
		wo.assigned_to = source.assigned_to

	if getattr(source, "pmc_property_unit", None):
		wo.pmc_property_unit = source.pmc_property_unit
	if getattr(source, "re_unit_inventory", None):
		wo.re_unit_inventory = source.re_unit_inventory
	if source.subject_doctype and source.subject_name:
		wo.subject_doctype = source.subject_doctype
		wo.subject_name = source.subject_name
	elif source.premises_doctype and source.premises_name:
		wo.subject_doctype = source.premises_doctype
		wo.subject_name = source.premises_name

	desc = strip_html(source.description or "").strip()
	if desc:
		wo.description = desc[:4000]

	wo.insert(ignore_permissions=False)

	return wo.name


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("maintenance_core", scenario=scenario, params=params)
