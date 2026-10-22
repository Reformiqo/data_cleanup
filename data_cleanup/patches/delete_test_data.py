# Deletes all test data from the gold-loan site.
#
# As a patch: copy into <app>/patches/ and add "<app>.patches.delete_test_data" to patches.txt.
# One-off:    bench --site <site> console, paste this file, then call execute().
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
	# Clear old error logs first, so the errors logged by this run are kept
	frappe.db.delete("Error Log")
	frappe.db.commit()

	for doctype in DOCTYPES:
		if not frappe.db.exists("DocType", doctype):
			continue

		meta = frappe.get_meta(doctype)

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
			try:
				# Delete child table rows first, then the parent records
				for table_field in meta.get_table_fields():
					frappe.db.delete(table_field.options, {"parenttype": doctype})

				frappe.db.delete(doctype)
				frappe.db.commit()
			except Exception:
				frappe.db.rollback()
				frappe.log_error(title=f"Could not delete {doctype}")
				frappe.db.commit()