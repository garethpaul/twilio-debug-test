.PHONY: build check lint test verify

PYTHON ?= python3
NODE ?= node

lint:
	$(PYTHON) -m py_compile test.py tests/test_company_comms.py tests/test_docs_plans.py
	$(NODE) --check test.js
	$(NODE) --check tests/test_js_contracts.js

test: lint
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'
	$(NODE) tests/test_js_contracts.js

build: lint

verify: lint test build

check: verify
