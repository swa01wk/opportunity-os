#!/usr/bin/env bash
# Pin every image in infra/images.env and infra/ci/tools.env to its current digest
# and regenerate the lockfiles (uv.lock, pnpm-lock.yaml) inside containers (SPEC-01a, SPEC-02).
# Run after changing a tag or a dependency range; commit the results. Renovate takes over
# routine updates (ADR-019).
set -euo pipefail
cd "$(dirname "$0")/.."

pin_env_file() {
  local pins=$1
  ref() { sed -n "s/^$1=//p" "$pins"; }

  for name in $(sed -n 's/^\([A-Z_]*_IMAGE\)=.*/\1/p' "$pins"); do
    tag=$(ref "$name"); tag=${tag%@*}
    out=$(docker buildx imagetools inspect "$tag" 2>&1) || { echo "pin.sh: $tag: $out" >&2; exit 1; }
    digest=$(printf '%s\n' "$out" | awk '$1 == "Digest:" { print $2; exit }')
    [[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]] || {
      printf 'pin.sh: no digest for %s in:\n%s\n' "$tag" "$out" >&2
      exit 1
    }
    sed -i.bak "s|^$name=.*|$name=$tag@$digest|" "$pins" && rm -f "$pins.bak"
    echo "pinned $name=$tag@$digest"
  done
}

pin_env_file infra/images.env
pin_env_file infra/ci/tools.env

uv_version=$(sed -n 's/^UV_IMAGE=.*:\([^@]*\)@.*/\1/p' infra/images.env | head -1)
docker run --rm -v "$PWD:/repo" -w /repo "$(sed -n 's/^PYTHON_IMAGE=//p' infra/images.env | head -1)" \
  sh -c "pip install --quiet --root-user-action=ignore uv==$uv_version && uv lock"
docker run --rm -v "$PWD:/repo" -w /repo -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 "$(sed -n 's/^NODE_IMAGE=//p' infra/images.env | head -1)" \
  sh -c 'corepack enable && pnpm install --lockfile-only'
echo "pin.sh: done; review and commit infra/images.env, infra/ci/tools.env, uv.lock and pnpm-lock.yaml"