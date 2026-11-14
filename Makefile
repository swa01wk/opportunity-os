# OpportunityOS command surface (PROCESS.md "Make and Docker", ADR-019, ADR-022).
# Every target runs inside containers; the host needs only Docker, make and git.
SHELL := /bin/bash
.DEFAULT_GOAL := help

include infra/images.env

COMPOSE_PROJECT ?= oos-dev
export GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
export HOST_UID := $(shell id -u)
export HOST_GID := $(shell id -g)

COMPOSE := docker compose --project-name $(COMPOSE_PROJECT) --env-file infra/images.env --env-file .env
PY := $(COMPOSE) run --rm --no-deps py-tools
TS := $(COMPOSE) run --rm --no-deps ts-tools

# Steps `make check` runs, in order; CI calls the same target (SPEC-02).
CHECK_STEPS ?= py-lint py-format py-types py-test ts-lint ts-format ts-types ts-test

.PHONY: help setup up down migrate seed lint fmt test test-int test-e2e eval check \
	contracts r0-sample release deploy promote

help: ## List the targets
	@grep -E '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/^[^:]*:([a-z0-9-]+):.*## /\1\t/; s/^([a-z0-9-]+):.*## /\1\t/' \
		| awk -F'\t' '{ printf "  %-12s %s\n", $$1, $$2 }'

.env:
	@echo "No .env: run make setup first."; exit 1

# Never overwrites an existing .env (AC3).
_env-file:
	@if [ -f .env ]; then echo "make setup: .env exists, left unchanged"; \
	else cp .env.example .env && echo "make setup: created .env from .env.example"; fi

setup: _env-file ## First run: create .env if absent, build images, install the gitleaks pre-commit hook
	$(COMPOSE) pull --ignore-buildable --quiet
	$(COMPOSE) --profile tools build
	docker pull --quiet $(GITLEAKS_IMAGE)
	git config core.hooksPath infra/git-hooks
	@echo "make setup: done; next: make up"

up: .env ## Start the local stack and wait until every service is healthy
	$(COMPOSE) up --detach --build --wait --wait-timeout 600

down: .env ## Stop the stack, keeping named volumes; CLEAN=1 also removes them
	$(COMPOSE) --profile tools down --remove-orphans $(if $(CLEAN),--volumes)

migrate: .env ## Apply database migrations (Alembic upgrade head)
	$(COMPOSE) run --rm migrate

seed: ## Load synthetic fixtures (no-op until SPEC-04)
	@echo "make seed: no fixtures yet (SPEC-04)"

lint: .env ## Lint, format check and type check every layer
	@$(MAKE) --no-print-directory check CHECK_STEPS="py-lint py-format py-types ts-lint ts-format ts-types"

fmt: .env ## Format every layer in place
	$(PY) ruff check --fix .
	$(PY) ruff format .
	$(TS) pnpm format

test: .env ## Unit, component and contract tests of every layer
	@$(MAKE) --no-print-directory check CHECK_STEPS="py-test ts-test"

test-int: ## Playwright integration tests against the running stack
	@echo "make test-int: 0 suites (added with the first Playwright test)"

test-e2e: ## Playwright end-to-end tests against the running stack
	@echo "make test-e2e: 0 suites (added with the first Playwright test)"

eval: ## Agent evals, fake model by default (LIVE=1 for the real model)
	@echo "make eval: 0 suites"

check: ## Everything the PR checks run; names every failing step
	@failed=""; for step in $(CHECK_STEPS); do \
		echo "==> make check: $$step"; \
		$(MAKE) --no-print-directory _step-$$step || failed="$$failed $$step"; \
	done; \
	if [ -n "$$failed" ]; then echo "make check: FAILED at step(s):$$failed"; exit 1; fi; \
	echo "make check: all steps passed ($(CHECK_STEPS))"

_step-py-lint: ; $(PY) ruff check .
_step-py-format: ; $(PY) ruff format --check .
_step-py-types: ; $(PY) mypy
_step-py-test: ; $(PY) pytest
_step-ts-lint: ; $(TS) pnpm lint
_step-ts-format: ; $(TS) pnpm format:check
_step-ts-types: ; $(TS) pnpm typecheck
_step-ts-test: ; $(TS) pnpm test
# Used by the T-31 check that a failing step is named (e2e/nfr/test_make_targets.py).
_step-selftest-pass: ; @true
_step-selftest-fail: ; @false

# Targets owned by later specs (AC5).
contracts: ## Regenerate JSON Schema and TS types (SPEC-03a)
	@echo "make contracts: not implemented yet; SPEC-03a implements it"; exit 1
r0-sample: ## The R0 odd-squares pipeline (SPEC-25)
	@echo "make r0-sample: not implemented yet; SPEC-25 implements it"; exit 1
release: ## Build every image once and write the release record (SPEC-01b)
	@echo "make release: not implemented yet; SPEC-01b implements it"; exit 1
deploy: ## Deploy a release to staging (SPEC-01b)
	@echo "make deploy: not implemented yet; SPEC-01b implements it"; exit 1
promote: ## Promote a verified release by digest (SPEC-01b)
	@echo "make promote: not implemented yet; SPEC-01b implements it"; exit 1
