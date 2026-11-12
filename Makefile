# Stub. Targets are implemented in M0 (PROCESS.md "Make and Docker").
TARGETS := setup up down migrate seed lint fmt test test-int test-e2e eval check

.PHONY: help $(TARGETS)

help:
	@echo "Targets (implemented in M0): $(TARGETS)"

$(TARGETS):
	@echo "make $@: not implemented yet (built in M0)"; exit 1
