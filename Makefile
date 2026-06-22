.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check lint node-package-check package-check root-test test verify

PUBLIC_TARGETS := build check lint node-package-check package-check root-test test verify

PYTHON ?= python3
NODE ?= node
NPM ?= npm
override PYTHON := $(value PYTHON)
override NODE := $(value NODE)
override NPM := $(value NPM)
export PYTHON NODE NPM
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value PYTHON)),)
$(error PYTHON must be a literal executable path, not Make syntax)
endif
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value NODE)),)
$(error NODE must be a literal executable path, not Make syntax)
endif
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value NPM)),)
$(error NPM must be a literal executable path, not Make syntax)
endif
override SHELL := /bin/sh
override .SHELLFLAGS := -c

ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(filter --just-print --dry-run --recon --touch --question --ignore-errors,$(MAKEFLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override REPOSITORY_MAKEFILE := $(lastword $(MAKEFILE_LIST))
override REPOSITORY_ROOT := $(abspath $(dir $(REPOSITORY_MAKEFILE)))
override ROOT := $(REPOSITORY_ROOT)
export ROOT

$(PUBLIC_TARGETS): override SHELL := /bin/sh
$(PUBLIC_TARGETS): override .SHELLFLAGS := -c
$(PUBLIC_TARGETS): override ROOT := $(REPOSITORY_ROOT)
$(PUBLIC_TARGETS): __repository-make-authority

__repository-make-authority:
	@:

lint:
	cd "$$ROOT" && "$$PYTHON" -m py_compile test.py tests/test_company_comms.py tests/test_docs_plans.py
	cd "$$ROOT" && "$$NODE" --check test.js
	cd "$$ROOT" && "$$NODE" --check tests/test_js_contracts.js
	cd "$$ROOT" && "$$NODE" scripts/check-node-package.js

test: lint
	cd "$$ROOT" && "$$PYTHON" -m unittest discover -s tests -p 'test_*.py'
	cd "$$ROOT" && "$$NODE" tests/test_js_contracts.js

build: lint

verify: lint test build

node-package-check:
	cd "$$ROOT" && "$$NPM" ci --ignore-scripts --no-audit --fund=false
	cd "$$ROOT" && "$$NPM" audit --omit=dev --audit-level=low

package-check: node-package-check
	PYTHON="$$PYTHON" "$$ROOT/scripts/check-python-package.sh"

root-test:
	/bin/sh "$$ROOT/scripts/test-makefile-authority.sh"

check: root-test verify package-check
	"$$ROOT/scripts/check-baseline.sh"
