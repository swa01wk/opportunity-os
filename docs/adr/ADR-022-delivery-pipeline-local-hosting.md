# ADR-022: Delivery pipeline and environments while hosting is local
Status: Accepted (tech lead, Stage 3; you confirm at G3)    Date: 2026-11-14

## Context
PROCESS.md (CI/CD pipeline) promotes one build artifact from PR to dev, staging and production, with feature flags and a rollback ready, and conformance C14 blocks a deployed build that differs from the verified one. ADR-011 keeps hosting on your machine until the R2 gate: there is no public endpoint, and GitHub-hosted runners cannot reach the machine. NFR-13 asks for reproducible local and staging environments with separate credentials and reviewed migrations with a tested rollback; NFR-14 for backups; SECURITY.md for per-environment secrets. Rendering images (Node, Chrome, Remotion) are large, so pushing every build to a private registry would eat into GitHub's package storage allowance.

## Decision
- **CI verifies; it does not deploy.** PR, main, nightly and weekly jobs run on GitHub-hosted runners in an ephemeral Compose stack with fake providers. Main builds every image and smoke-tests it; that ephemeral stack stands in for the PROCESS "dev" deploy. Live provider calls in CI happen only in the weekly and labelled eval jobs, with separate keys that have spend caps.
- **Your machine is the release host.** `make release VERSION=vX.Y.Z[-rc.N]` builds every image once, from a clean checkout of the tag, with locked dependencies and base images pinned by digest, and writes `releases/<version>.json` (commit, image digests, contracts version, migration head). Images stay in the local Docker image store; a `docker save` archive of the previous release is kept for rollback.
- **Environments are separate Compose projects on that machine:** `oos-dev` (`make up`, feature branches, fakes by default), `oos-staging` (release candidates), `oos-prod` (from go-live, G5). Each has its own `.env.<env>`, database, bucket, Keycloak realm and provider keys (NFR-13).
- **Promotion is by digest.** `make deploy ENV=staging VERSION=…` starts exactly the recorded digests and runs migrations; the milestone suite runs there. `make promote VERSION=…` refuses unless the digests equal the release record verified on staging (C14), takes a pre-migration snapshot (SECURITY.md backups), migrates, starts and smoke-tests. Rollback is `make promote VERSION=<previous>` plus the migration downgrade tested in CI.
- **Feature flags are environment variables** (`FEATURE_*` in `.env.example`) read at start-up. No flag service.
- **No self-hosted runner** and no image registry while there is one host.
- **On the AWS move** (after the R2 gate, ADR-011), CI pushes images to ECR and deploys from the pipeline; the release record format stays.

## Alternatives
- **Self-hosted GitHub runner on your machine:** deploys from CI, but runs PR code on the machine that holds production data and credentials.
- **Push every build to GitHub Container Registry and pull on deploy:** one artifact end to end, but multi-gigabyte render images exceed the private package storage allowance and add cost before there is any hosting need.
- **Rebuild per environment:** simplest, but staging and production would run different builds, which C14 forbids.

## Consequences
- Easier: no inbound access to your machine; no registry cost; the artifact verified on staging is the one that runs in production.
- Harder: releases are run by hand from the machine; CI's image build proves buildability, not the release artifact itself, so the release build must be reproducible (pinned base digests and lockfiles). Three Compose projects compete for one machine's memory, so staging runs only while a release candidate is being verified.
- Must do: SPEC-01 adds `make release`, `make deploy`, `make promote`; SPEC-02 adds the CI jobs and required checks; SPEC-13 deploys the walking skeleton to staging; SPEC-83 adds the C12 and C14 release checks. TEST_STRATEGY.md owns the environment table and cadence.
