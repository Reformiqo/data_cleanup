# Deletes all test data from the gold-loan site.
#
# Runs inside install or migrate, not in a background job:
# - after_install runs it when the app is installed (Frappe marks an app's patches as done on install).
# - patches.txt runs it on the next migrate for sites that already have the app. To run it again,
#   change the "#<date>" after its line in patches.txt and migrate (deploy on Frappe Cloud).
#
# Take a backup first: bench --site <site> backup

import frappe

# Child-most doctypes first so nothing is left pointing at a deleted parent
DOCTYPES = [
	"Auction Paper Notification",
	"Auction Notice",
	"Auction Case",
	"Auction Event",
	"Loan Write Off",
	"Gold Release Request",
	"Process Collection Dunning",
	"Loan Repayment",
	"Loan Demand Offset Order",
	"Loan Demand",
	"Loan Interest Accrual",
	"Days Past Due Log",
	"Process Loan Interest Accrual",
	"Process Loan Demand",
	"Process Loan Classification",
	"Process Loan Security Shortfall",
	"Loan Security Shortfall",
	"Loan Disbursement",
	"Loan Repayment Schedule",
	"Loan",
	"Loan Security Assignment",
	"Loan Application",
	"Loan Security Price",
	"Loan Security",
	"Key Facts Statement",
	"Gold Packet",
	"Vault Movement",
	"Vault Audit",
	"Gold Appraisal",
	"Credit Assessment",
	"Cooling Off Case",
	"Customer Risk Event",
	"Consent Log",
	"Gold OTP Request",
	"Digio Request Log",
	"Regulatory Filing Log",
	"KYC Profile",
	"Loan Lead",
	"Customer",
	"Contact",
	"Kotak CMS Payment Request",
	"Process Subscription",
	"Process Deferred Accounting",
	"Assistant Audit Log",
	"Comment",
	"ToDo",
	"Notification Log",
	"Email Queue",
	"Email Unsubscribe",
	"Error Log",
	"Scheduled Job Log",
	"Integration Request Log",
	"Route History",
	"Activity Log",
	"Access Log",
	"Permission Log",
	"Console Log",
	"Version",
	"Deleted Document",
]


def execute():
	# Cancelling loans must not email or notify customers
	frappe.flags.mute_emails = True

	# Clear old error logs first, so the errors logged by this run are kept
	frappe.db.delete("Error Log")
	frappe.db.commit()

	for doctype in DOCTYPES:
		try:
			delete_doctype(doctype)
		except Exception:
			# One bad doctype must not stop the rest
			frappe.db.rollback()
			frappe.log_error(title=f"Could not delete {doctype}")
			frappe.db.commit()

	log_summary()


def delete_doctype(doctype):
	if not frappe.db.exists("DocType", doctype):
		return

	meta = frappe.get_meta(doctype)
	if meta.issingle or meta.is_virtual:
		return

	if meta.is_submittable:
		# Cancel submitted documents first so their ledger entries get reversed
		for name in frappe.get_all(doctype, pluck="name"):
			try:
				doc = frappe.get_doc(doctype, name)
				if doc.docstatus == 1:
					doc.flags.ignore_permissions = True
					doc.flags.ignore_links = True
					doc.cancel()

				frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
				frappe.db.commit()
			except Exception:
				frappe.db.rollback()
				frappe.log_error(title=f"Could not delete {doctype} {name}")
				frappe.db.commit()
	else:
		# Delete child table rows first, then the parent records
		for table_field in meta.get_table_fields():
			frappe.db.delete(table_field.options, {"parenttype": doctype})

		frappe.db.delete(doctype)
		frappe.db.commit()


def log_summary():
	# Report the result in the migrate output and in Error Log
	left = {}
	for doctype in DOCTYPES:
		if doctype in ("Error Log", "Deleted Document"):
			continue
		try:
			if frappe.db.exists("DocType", doctype) and not frappe.get_meta(doctype).is_virtual:
				count = frappe.db.count(doctype)
				if count:
					left[doctype] = count
		except Exception:
			pass

	if left:
		lines = "\n".join(f"{doctype}: {count}" for doctype, count in left.items())
		title = f"Data Cleanup finished: {sum(left.values())} records could not be deleted"
		message = f"Records still on the site:\n{lines}\n\nSee the other Error Log entries for why."
	else:
		title = "Data Cleanup finished: all records deleted"
		message = "All listed doctypes are empty."

	print(title)
	frappe.log_error(title=title, message=message)
	frappe.db.commit()
