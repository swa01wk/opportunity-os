# OpportunityOS command surface (PROCESS.md "Make and Docker", ADR-019, ADR-022).
# Every target runs inside containers; the host needs only Docker, make and git.
SHELL := /bin/bash
.DEFAULT_GOAL := help

include infra/images.env
-include infra/ci/tools.env

COMPOSE_PROJECT ?= oos-dev
export GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
export HOST_UID := $(shell id -u)
export HOST_GID := $(shell id -g)

COMPOSE := docker compose --project-name $(COMPOSE_PROJECT) --env-file infra/images.env --env-file .env
PY := $(COMPOSE) run --rm --no-deps py-tools
PY_AUDIT := $(COMPOSE) run --rm --no-deps py-audit
PY_FUNC := $(COMPOSE) run --rm --no-deps -e OOS_HOST_REPO=$(CURDIR) py-functional
TS := $(COMPOSE) run --rm --no-deps ts-tools

# Steps `make check` runs, in order; CI calls the same target (SPEC-02).
CHECK_STEPS ?= py-lint py-format py-types py-test py-functional ts-lint ts-format ts-types ts-test
# ci-security runs every sub-check and lists all failures (SPEC-02 B9).
SECURITY_CHECK_STEPS ?= verify-action-pins actionlint gitleaks gitleaks-fixture semgrep \
	pip-audit pnpm-audit trivy licences

.PHONY: help setup up down migrate seed lint fmt test test-int test-e2e eval check \
	contracts contracts-check _contracts-drift r0-sample release deploy promote \
	ci-lint ci-types ci-test-backend ci-test-agent ci-test-media ci-test-web \
	ci-contracts ci-conformance ci-e2e-smoke ci-render-fixture ci-migrations ci-images ci-security \
	ci-smoke-readyz _step-verify-action-pins _step-actionlint _step-gitleaks _step-gitleaks-fixture \
	_step-semgrep _step-pip-audit _step-pnpm-audit _step-trivy _step-licences

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

seed: .env ## Load synthetic fixtures (dev and staging only; refuses in production)
	$(COMPOSE) run --rm seed

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
_step-py-test: ; $(PY) pytest -m "not functional"
_step-py-functional: ; $(PY_FUNC) pytest -m functional
_step-ts-lint: ; $(TS) pnpm lint
_step-ts-format: ; $(TS) pnpm format:check
_step-ts-types: ; $(TS) pnpm typecheck
_step-ts-test: ; $(TS) pnpm test
# Used by the T-31 check that a failing step is named (e2e/nfr/test_make_targets.py).
_step-selftest-pass: ; @true
_step-selftest-fail: ; @false

contracts: .env ## Regenerate JSON Schema and TypeScript types from Pydantic (SPEC-03a)
	$(PY) python -m opportunityos_contracts._build
	$(TS) pnpm --filter @oos/contracts run generate
	$(TS) pnpm exec prettier --write contracts/ts/src/generated contracts/ts/src/index.ts

_contracts-drift: ## Fail when generated contract files differ from git (SPEC-03a AC2)
	@status=$$(git status --porcelain -- docs/contracts contracts/ts/src); \
	if [ -n "$$status" ]; then \
	  echo "make contracts-check: drift detected:"; \
	  echo "$$status" | awk '{print $$2}'; \
	  git diff --stat -- docs/contracts contracts/ts/src; \
	  git diff -- docs/contracts contracts/ts/src | head -n 60; \
	  exit 1; \
	fi

contracts-check: contracts ## Fail when generated contracts drift from the repo
	@$(MAKE) _contracts-drift
r0-sample: ## The R0 odd-squares pipeline (SPEC-25)
	@echo "make r0-sample: not implemented yet; SPEC-25 implements it"; exit 1
release: ## Build every image once and write the release record (SPEC-01b)
	@echo "make release: not implemented yet; SPEC-01b implements it"; exit 1
deploy: ## Deploy a release to staging (SPEC-01b)
	@echo "make deploy: not implemented yet; SPEC-01b implements it"; exit 1
promote: ## Promote a verified release by digest (SPEC-01b)
	@echo "make promote: not implemented yet; SPEC-01b implements it"; exit 1

# --- SPEC-02: GitHub Actions jobs call these targets (TEST_STRATEGY.md required checks). ---

ci-lint: .env ## PR job lint
	@$(MAKE) --no-print-directory _step-py-lint _step-py-format _step-ts-lint _step-ts-format

ci-types: .env ## PR job types
	@$(MAKE) --no-print-directory _step-py-types _step-ts-types

ci-test-backend: .env ## PR job test-backend (unit, functional, diff-cover)
	@$(MAKE) --no-print-directory _step-py-test-backend _step-py-functional _step-diff-cover-backend

ci-test-agent: .env ## PR job test-agent
	@$(PY) pytest agent/tests -q

ci-test-media: .env ## PR job test-media
	@$(PY) pytest media/audio/tests -q
	@$(TS) pnpm --filter @oos/scenes test

ci-test-web: .env ## PR job test-web
	@$(TS) pnpm --filter @oos/web test
	@$(MAKE) --no-print-directory _step-diff-cover-web

ci-contracts: .env ## PR job contracts
	@$(MAKE) contracts-check
	@$(PY) pytest contracts/tests -q

ci-conformance: .env ## PR job conformance
	@echo "ci-conformance: 0 tests"
	@exit 0

ci-e2e-smoke: .env ## PR job e2e-smoke
	@echo "ci-e2e-smoke: 0 tests"
	@exit 0

ci-render-fixture: .env ## PR job render-fixture
	@echo "ci-render-fixture: 0 tests"
	@exit 0

ci-migrations: .env ## PR job migrations up, down, re-up
	$(COMPOSE) up -d postgres --wait
	@$(MAKE) migrate
	$(COMPOSE) run --rm --no-deps migrate alembic -c backend/alembic.ini downgrade base
	@$(MAKE) migrate
	$(COMPOSE) stop postgres

ci-images: setup ## PR job image build
	$(COMPOSE) --profile tools build

ci-smoke-readyz: .env ## Main workflow: /readyz on api, worker, render and web (ADR-022)
	@compose=(docker compose --project-name $(COMPOSE_PROJECT) --env-file infra/images.env --env-file .env); \
	py_probe='import os,sys,urllib.request as u; u.urlopen("http://127.0.0.1:"+os.environ["PORT"]+"/readyz"); sys.exit(0)'; \
	node_probe='fetch(`http://127.0.0.1:$${process.env.PORT}/readyz`).then(r=>process.exit(r.ok?0:1),()=>process.exit(1))'; \
	for service in api worker; do "$${compose[@]}" exec -T "$$service" python -c "$$py_probe" || exit 1; done; \
	for service in render web; do "$${compose[@]}" exec -T "$$service" node -e "$$node_probe" || exit 1; done

ci-security: setup ## PR job gitleaks, Semgrep, audits, Trivy, licences
	@failed=""; for step in $(SECURITY_CHECK_STEPS); do \
		echo "==> ci-security: $$step"; \
		$(MAKE) --no-print-directory _step-$$step || failed="$$failed $$step"; \
	done; \
	if [ -n "$$failed" ]; then echo "ci-security: FAILED at step(s):$$failed"; exit 1; fi; \
	echo "ci-security: all steps passed ($(SECURITY_CHECK_STEPS))"

_step-py-test-backend: ; $(PY) pytest backend/tests -m "not functional" -q

_step-diff-cover-backend:
	@$(PY) pytest backend/tests -m "not functional" \
		--cov=backend/opportunityos/domain --cov-report=xml:coverage.xml \
		--cov-report=term-missing -q --cov-fail-under=0
	@$(PY) diff-cover coverage.xml \
		--compare-branch=origin/main --fail-under=80

_step-diff-cover-web:
	@echo "diff-cover: 0 web components yet (70% floor when web/components/ exists)"

_step-verify-action-pins:
	@python3 "$(CURDIR)/infra/ci/verify_action_pins.py"

_step-actionlint:
	@if [ -z "$(ACTIONLINT_IMAGE)" ]; then echo "ACTIONLINT_IMAGE unset"; exit 1; fi
	@docker run --rm -v "$(CURDIR):/repo:ro" -w /repo "$(ACTIONLINT_IMAGE)" -color

_step-gitleaks:
	@docker run --rm -v "$(CURDIR):/repo:ro" -w /repo "$(GITLEAKS_IMAGE)" \
		git --redact=100 --no-banner -v /repo \
		-c /repo/infra/ci/gitleaks/.gitleaks.toml

_step-gitleaks-fixture:
	@$(PY_FUNC) python /repo/infra/ci/gitleaks/verify_fixture.py

_step-semgrep:
	@docker run --rm -v "$(CURDIR):/src:ro" -w /src "$(SEMGREP_IMAGE)" \
		semgrep --test --config /src/infra/ci/semgrep/rules /src/infra/ci/semgrep/tests
	@docker run --rm -v "$(CURDIR):/src:ro" -w /src "$(SEMGREP_IMAGE)" semgrep --error \
		--config /src/infra/ci/semgrep/rules --exclude /src/infra/ci/semgrep/tests /src

_step-pip-audit: ; $(PY_AUDIT) pip-audit

_step-pnpm-audit: ; $(TS) pnpm audit --audit-level high

_step-trivy:
	@$(MAKE) ci-images
	@for img in oos/api:dev oos/worker:dev oos/web:dev oos/render:dev oos/objectstore:interim; do \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$(CURDIR):/repo:ro" \
			"$(TRIVY_IMAGE)" image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed \
			--ignorefile /repo/infra/ci/.trivyignore.yaml "$$img"; \
	done

_step-licences:
	@$(PY) python /repo/infra/ci/check_licences.py --python-only
	@$(TS) sh -c 'pnpm licenses list --json > /repo/infra/ci/.pnpm-licenses.json'
	@$(PY) python /repo/infra/ci/check_licences.py --pnpm-json /repo/infra/ci/.pnpm-licenses.json
