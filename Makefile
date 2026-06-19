.PHONY: build check lint node-package-check package-check test verify

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3
NODE ?= node
NPM ?= npm

lint:
	cd "$(ROOT)" && $(PYTHON) -m py_compile test.py tests/test_company_comms.py tests/test_docs_plans.py
	cd "$(ROOT)" && $(NODE) --check test.js
	cd "$(ROOT)" && $(NODE) --check tests/test_js_contracts.js
	cd "$(ROOT)" && $(NODE) scripts/check-node-package.js

test: lint
	cd "$(ROOT)" && $(PYTHON) -m unittest discover -s tests -p 'test_*.py'
	cd "$(ROOT)" && $(NODE) tests/test_js_contracts.js

build: lint

verify: lint test build

node-package-check:
	cd "$(ROOT)" && $(NPM) ci --ignore-scripts --no-audit --fund=false
	cd "$(ROOT)" && $(NPM) audit --omit=dev --audit-level=low

package-check: node-package-check
	PYTHON="$(PYTHON)" "$(ROOT)/scripts/check-python-package.sh"

check: verify package-check
	"$(ROOT)/scripts/check-baseline.sh"
