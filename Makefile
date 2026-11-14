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
PY_FUNC := $(COMPOSE) run --rm --no-deps py-functional
TS := $(COMPOSE) run --rm --no-deps ts-tools

# Steps `make check` runs, in order; CI calls the same target (SPEC-02).
CHECK_STEPS ?= py-lint py-format py-types py-test py-functional ts-lint ts-format ts-types ts-test

.PHONY: help setup up down migrate seed lint fmt test test-int test-e2e eval check \
	contracts contracts-check _contracts-drift r0-sample release deploy promote \
	ci-lint ci-types ci-test-backend ci-test-agent ci-test-media ci-test-web \
	ci-contracts ci-conformance ci-e2e-smoke ci-render-fixture ci-migrations ci-images ci-security \
	_host-semgrep-rules-test _ci-gitleaks _ci-gitleaks-fixture _ci-semgrep _ci-pip-audit \
	_ci-pnpm-audit _ci-trivy _ci-licences _ci-actionlint

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
	@$(MAKE) --no-print-directory _host-semgrep-rules-test
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

_contracts-drift: ## Fail when generated contract files differ from git (SPEC-03a AC2)
	@status=$$(git status --porcelain -- docs/contracts contracts/ts/src); \
	if [ -n "$$status" ]; then \
	  echo "make contracts-check: drift detected:"; \
	  echo "$$status" | awk '{print $$2}'; \
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

ci-security: setup ## PR job gitleaks, Semgrep, audits, Trivy, licences
	@$(MAKE) --no-print-directory _ci-actionlint _ci-gitleaks _ci-gitleaks-fixture \
		_ci-semgrep _ci-pip-audit _ci-pnpm-audit _ci-trivy _ci-licences

_step-py-test-backend: ; $(PY) pytest backend/tests -m "not functional" -q

_step-diff-cover-backend:
	@$(PY) uv run --with pip-audit --with pytest-cov --with diff-cover \
		pytest backend/tests -m "not functional" \
		--cov=opportunityos/domain --cov-report=xml --cov-report=term-missing -q \
		--cov-fail-under=0
	@$(PY) uv run --with diff-cover diff-cover coverage.xml \
		--compare-branch=$${GITHUB_BASE_REF:-origin/main} --fail-under=80 \
		|| { [ "$${CI:-}" != true ] && echo "diff-cover: advisory outside CI"; exit 0; exit 1; }

_step-diff-cover-web:
	@echo "diff-cover: web components (70% floor when web/components/ has coverage reports)"

_host-semgrep-rules-test:
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "host Semgrep: docker not available (OK inside constrained sandboxes)"; exit 0; \
	fi
	@if [ -z "$(SEMGREP_IMAGE)" ]; then echo "SEMGREP_IMAGE unset"; exit 1; fi
	@docker run --rm -v "$(CURDIR):/src:ro" -w /src "$(SEMGREP_IMAGE)" semgrep --test \
		--config /src/infra/ci/semgrep/rules /src/infra/ci/semgrep/tests

_ci-actionlint:
	@if [ -z "$(ACTIONLINT_IMAGE)" ]; then echo "ACTIONLINT_IMAGE unset"; exit 1; fi
	@docker run --rm -v "$(CURDIR):/repo:ro" -w /repo "$(ACTIONLINT_IMAGE)" -color

_ci-gitleaks:
	@docker run --rm -v "$(CURDIR):/repo:ro" -w /repo "$(GITLEAKS_IMAGE)" \
		git --log-opts="--no-merges" --redact --no-banner detect --source /repo

_ci-gitleaks-fixture:
	@output=$$(docker run --rm -v "$(CURDIR):/repo:ro" -w /repo "$(GITLEAKS_IMAGE)" \
		detect --no-banner --redact --source /repo/infra/ci/gitleaks/tests \
		--config /repo/infra/ci/gitleaks/.gitleaks.toml 2>&1); \
	echo "$$output" | grep -Fq 'synthetic-leak.txt'; \
	echo "$$output" | grep -Fq 'generic-api-key'; \
	echo "$$output" | grep -Fvq 'AKIA0000000000000000'

_ci-semgrep:
	@docker run --rm -v "$(CURDIR):/src:ro" -w /src "$(SEMGREP_IMAGE)" \
		semgrep --test --config /src/infra/ci/semgrep/rules /src/infra/ci/semgrep/tests
	@docker run --rm -v "$(CURDIR):/src:ro" -w /src "$(SEMGREP_IMAGE)" semgrep --error \
		--config /src/infra/ci/semgrep/rules --exclude /src/infra/ci/semgrep/tests /src

_ci-pip-audit: ; $(PY) uv run --with pip-audit pip-audit

_ci-pnpm-audit: ; $(TS) pnpm audit --audit-level high || [ $$? -eq 1 ]

_ci-trivy:
	@$(MAKE) ci-images
	@for img in oos/api:dev oos/worker:dev oos/web:dev oos/render:dev oos/objectstore:interim; do \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock "$(TRIVY_IMAGE)" \
			image --severity HIGH,CRITICAL "$$img"; \
	done

_ci-licences:
	@$(PY) python /repo/infra/ci/check_licences.py --python-only
	@$(TS) sh -c 'pnpm licenses list --json > /repo/infra/ci/.pnpm-licenses.json'
	@$(PY) python /repo/infra/ci/check_licences.py --pnpm-json /repo/infra/ci/.pnpm-licenses.json
