# Tenant maintenance intake

Log in as a user with role **Maintenance Portal User** (system user). Then call the authenticated REST API from your portal or mobile client.

**Create a service request**

`POST /api/method/erpgenex_maintenance_core.api.portal_create_service_request`

JSON body (example): `company`, `description`, optional `priority`, `branch`, optional `premises_doctype`, `premises_name`, optional `subject_doctype`, `subject_name`.

**List my requests**

`GET /api/method/erpgenex_maintenance_core.api.portal_get_my_service_requests`

**PMC units (property management)**

Desk users may call `erpgenex_property_mgmt.api.create_core_service_request_for_pmc_unit` to open a **Core Service Request** with `premises_doctype = PMC Property Unit`.

---

_This page is a lightweight website entry; full branding and Web Forms can be added per tenant._
