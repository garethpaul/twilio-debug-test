.PHONY: build check lint package-check test verify

ROOT := $(CURDIR)
PYTHON ?= python3
NODE ?= node

lint:
	cd "$(ROOT)" && $(PYTHON) -m py_compile test.py tests/test_company_comms.py tests/test_docs_plans.py
	cd "$(ROOT)" && $(NODE) --check test.js
	cd "$(ROOT)" && $(NODE) --check tests/test_js_contracts.js

test: lint
	cd "$(ROOT)" && $(PYTHON) -m unittest discover -s tests -p 'test_*.py'
	cd "$(ROOT)" && $(NODE) tests/test_js_contracts.js

build: lint

verify: lint test build

package-check:
	PYTHON="$(PYTHON)" "$(ROOT)/scripts/check-python-package.sh"

check: verify package-check
	"$(ROOT)/scripts/check-baseline.sh"
