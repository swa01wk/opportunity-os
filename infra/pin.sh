#!/usr/bin/env bash
# Pin every image in infra/images.env to its current digest and regenerate the lockfiles
# (uv.lock, pnpm-lock.yaml) inside containers, so the host needs only Docker (SPEC-01a).
# Run after changing a tag or a dependency range; commit the results. Renovate takes over
# routine updates (ADR-019).
set -euo pipefail
cd "$(dirname "$0")/.."
pins=infra/images.env

ref() { sed -n "s/^$1=//p" "$pins"; }

for name in $(sed -n 's/^\([A-Z_]*_IMAGE\)=.*/\1/p' "$pins"); do
  tag=$(ref "$name"); tag=${tag%@*}
  digest=$(docker buildx imagetools inspect "$tag" --format '{{.Manifest.Digest}}')
  [[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]] || { echo "pin.sh: could not resolve $tag" >&2; exit 1; }
  sed -i.bak "s|^$name=.*|$name=$tag@$digest|" "$pins" && rm -f "$pins.bak"
  echo "pinned $name=$tag@$digest"
done

uv_version=$(ref UV_IMAGE | sed -E 's/^[^:]+:([^@]+).*/\1/')
docker run --rm -v "$PWD:/repo" -w /repo "$(ref PYTHON_IMAGE)" \
  sh -c "pip install --quiet --root-user-action=ignore uv==$uv_version && uv lock"
docker run --rm -v "$PWD:/repo" -w /repo -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 "$(ref NODE_IMAGE)" \
  sh -c 'corepack enable && pnpm install --lockfile-only'
echo "pin.sh: done; review and commit infra/images.env, uv.lock and pnpm-lock.yaml"
