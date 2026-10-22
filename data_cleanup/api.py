import frappe
from frappe import _

from data_cleanup.patches import queue_data_cleanup


@frappe.whitelist(methods=["POST"])
def run_cleanup():
	"""Queue the data cleanup again. Administrator only, since it deletes all loan data."""
	if frappe.session.user != "Administrator":
		frappe.throw(_("Only Administrator can run the data cleanup."), frappe.PermissionError)

	queue_data_cleanup.execute()
	return _("Data cleanup queued. Check Error Log for the result when it finishes.")
