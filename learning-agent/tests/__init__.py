# Makes `tests/` a package so its modules import as `tests.test_*`, namespacing them
# away from repo-root `test_*.py` files (e.g. root test_assignments.py) and preventing
# pytest "import file mismatch" collection errors when a basename appears in two dirs.
# See pytest.ini for the historical _temp_hold/test_tenancy collision this guards against.
