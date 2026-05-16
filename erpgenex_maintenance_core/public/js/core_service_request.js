frappe.ui.form.on("Core Service Request", {
	refresh(frm) {
		if (frm.doc.__islocal) return;

		frm.add_custom_button(__("Core Work Order"), () => {
			frappe.call({
				method: "erpgenex_maintenance_core.api.make_core_work_order",
				args: { service_request: frm.doc.name },
				freeze: true,
				callback(r) {
					if (!r.exc && r.message) {
						frappe.set_route("Form", "Core Work Order", r.message);
					}
				},
			});
		}, __("Maintenance Core"));
	},
});
