# Queues the data cleanup as a background job instead of running it inside install or migrate,
# so a long run cannot time out or fail a Frappe Cloud deploy.
#
# Runs from after_install (fresh install) and from patches.txt (sites that already had the app,
# on their next migrate). Frappe marks patches as done on install, so it runs once either way.

import frappe


def execute():
	frappe.enqueue(
		"data_cleanup.patches.delete_test_data.execute",
		queue="long",
		timeout=6 * 60 * 60,
		job_id="data_cleanup",
		deduplicate=True,
	)
