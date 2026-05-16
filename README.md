### ERPGenEx Maintenance Core

Shared CMMS engine for fixed assets, property, rental, and facilities — **design cues from IBM Maximo** (SR → WO, failure taxonomy, PM, labour/material actuals, downtime) with traceability suited to **ISO 55000 / ISO 41001** style programmes.

**Standards mapping (detail):** see repo [`Docs/2026-05-15/audit/maintenance_standards_alignment.md`](../../../Docs/2026-05-15/audit/maintenance_standards_alignment.md).

### DocTypes

| DocType | Purpose |
|---------|---------|
| **Core SLA Profile** | Target response/resolution (hours). |
| **Core Service Request** | Intake; Dynamic Link **subject**; Company/Branch. |
| **Core Classification Code** | Maximo-style codes: Failure Class / Mode / Problem / Cause / Remedy / Symptom. |
| **Core Work Order** | Submittable WO; RCA links; downtime fields (MTTR support); labour/material tables; optional **PM Schedule** link. |
| **Core WO Labor Actual** | Child table — planned/actual hours, rate, labour cost. |
| **Core WO Material Actual** | Child table — optional **`Item`** link (`stock_item`); qty/rate/material cost. |
| **Core PM Schedule** | Calendar + **meter** PM vs **`Asset Meter Reading`**; **`run_daily_pm_generators`** (daily). |

**Dependency:** `omnexa_core`, **`omnexa_accounting`** (Item master for material lines).

**Package layout:** DocTypes under `erpgenex_maintenance_core/erpgenex_maintenance_core/erpgenex_maintenance_core/doctype/` (Frappe module scrub).

### Scheduler

`hooks.py` registers **`erpgenex_maintenance_core.tasks.run_daily_pm_generators`** (**daily**) — calendar PM + meter PM — requires **`bench schedule`**.

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench install-app erpgenex_maintenance_core
bench --site <site> migrate
```

### Contributing

Pre-commit (ruff, eslint, prettier, pyupgrade) — see `.pre-commit-config.yaml`.

### License

mit
