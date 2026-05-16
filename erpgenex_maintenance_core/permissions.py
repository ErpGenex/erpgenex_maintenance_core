import frappe


PORTAL_ROLE = "Maintenance Portal User"
# Desk / FM roles: full tenant list via standard DocPerm (no row-level filter from this module).
_FM_ROLES = frozenset({"System Manager", "Maintenance Manager", "Desk User"})


def _is_portal_scoped_user(user: str | None) -> bool:
	"""Users with only the portal maintenance role (plus global automatic roles) see their own CSRs."""
	if not user or user == "Administrator":
		return False
	roles = set(frappe.get_roles(user))
	if PORTAL_ROLE not in roles:
		return False
	if roles & _FM_ROLES:
		return False
	return True


def get_core_service_request_query_conditions(user, doctype=None) -> str:
	if not _is_portal_scoped_user(user):
		return ""
	return f"`tabCore Service Request`.`raised_by` = {frappe.db.escape(user)}"


def core_service_request_has_permission(doc, ptype=None, user=None, debug=False):
	"""Restrict portal tenants to Core Service Requests they raised."""
	if not user:
		user = frappe.session.user
	if user == "Administrator":
		return True
	if not _is_portal_scoped_user(user):
		return None
	if not doc:
		return None
	if (doc.get("raised_by") or "").lower() == (user or "").lower():
		return True
	return False
