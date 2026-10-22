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

The cleanup runs straight away, not as a background job:

- Installing the app on a site runs it once (`after_install`).
- A site that already had the app runs it once as a patch on its next migrate (on Frappe Cloud, the next deploy).
- To run it again, change the `#<date>` after `data_cleanup.patches.delete_test_data` in `patches.txt`
  and migrate (or deploy) again. Locally you can also run
  `bench --site <site> execute data_cleanup.patches.delete_test_data.execute`.

When it finishes, the migrate output and **Error Log** show `Data Cleanup finished: ...`, which says
whether everything was deleted or lists what is left; other Error Log entries say why a record could
not be deleted.

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
