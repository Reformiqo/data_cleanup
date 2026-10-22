### Data Cleanup

clear data in site

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch master
bench install-app data_cleanup
```

### What it does

Deletes all loan, customer, KYC, gold and log records listed in
`data_cleanup/patches/delete_test_data.py`. This cannot be undone: take a backup first.

The cleanup runs as a background job on the `long` queue:

- Installing the app on a site queues it once.
- A site that already had the app queues it once on its next migrate (on Frappe Cloud, the next deploy).
- To run it again, log in as Administrator and run this in the browser console:

```js
frappe.call({ method: "data_cleanup.api.run_cleanup", type: "POST" }).then((r) => console.log(r.message));
```

When the job finishes, open **Error Log**. An entry titled `Data Cleanup finished: ...` says whether
everything was deleted or lists what is left; other entries say why a record could not be deleted.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/data_cleanup
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
