#!/usr/bin/env bash
# T-31 (NFR-13; SPEC-01a AC1, AC2, AC6): a fresh clone on a host with only Docker, make and
# git reaches a healthy stack and a green make check with no manual step, then cleans up.
# Usage: e2e/nfr/fresh-clone.sh [branch]   (defaults to the current branch of this checkout)
set -euo pipefail

here=$(cd "$(dirname "$0")/../.." && pwd)
branch=${1:-$(git -C "$here" rev-parse --abbrev-ref HEAD)}
repo=${REPO_URL:-$(git -C "$here" remote get-url origin)}
project=oos-dev
workdir=$(mktemp -d)

step() { printf '\n==> T-31: %s\n' "$*"; }
fail() { printf 'T-31 FAILED: %s\n' "$*" >&2; exit 1; }
volumes() { docker volume ls --quiet --filter "label=com.docker.compose.project=$project"; }

if [ -n "$(docker compose --project-name "$project" ps --quiet 2>/dev/null)" ]; then
  fail "the $project stack is running; stop it (make down) before T-31, which uses the same ports"
fi
if [ -n "$(volumes)" ]; then
  fail "$project volumes exist; T-31 needs a clean host (make down CLEAN=1 removes them)"
fi

cleanup() {
  if [ -f "$workdir/oos/.env" ]; then make -C "$workdir/oos" down CLEAN=1 >/dev/null 2>&1 || true; fi
  rm -rf "$workdir"
}
trap cleanup EXIT

step "clone $repo@$branch"
git clone --quiet --depth 1 --branch "$branch" "$repo" "$workdir/oos"
cd "$workdir/oos"

step "make setup"
make setup
[ -f .env ] || fail "make setup did not create .env"

step "make up (waits for every service to be healthy)"
make up

step "every service reports healthy (AC1)"
compose=(docker compose --project-name "$project" --env-file infra/images.env --env-file .env)
expected=$("${compose[@]}" config --services | sort)
for service in $expected; do
  id=$("${compose[@]}" ps --quiet "$service")
  [ -n "$id" ] || fail "$service is not running"
  health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$id")
  [ "$health" = healthy ] || fail "$service is $health"
  echo "  $service: healthy"
done

step "/healthz returns 200 on api, worker, render and web (AC1)"
py_probe='import os,sys,urllib.request as u; sys.exit(0 if u.urlopen(f"http://127.0.0.1:{os.environ[\"PORT\"]}/healthz").status == 200 else 1)'
node_probe='fetch(`http://127.0.0.1:${process.env.PORT}/healthz`).then(r => process.exit(r.status === 200 ? 0 : 1), () => process.exit(1))'
for service in api worker; do "${compose[@]}" exec -T "$service" python -c "$py_probe" || fail "$service /healthz"; echo "  $service: 200"; done
for service in render web; do "${compose[@]}" exec -T "$service" node -e "$node_probe" || fail "$service /healthz"; echo "  $service: 200"; done

step "make check (AC2)"
make check

step "make down keeps named volumes (AC6)"
make down
[ -n "$(volumes)" ] || fail "make down removed the named volumes"

step "make down CLEAN=1 removes them (AC6)"
make down CLEAN=1
[ -z "$(volumes)" ] || fail "make down CLEAN=1 left volumes: $(volumes | tr '\n' ' ')"

printf '\nT-31 passed: fresh clone of %s is healthy and make check is green.\n' "$branch"
