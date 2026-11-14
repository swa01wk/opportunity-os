# check=skip=InvalidDefaultArgInFrom
# render (media/scenes, ADR-002). The service has no npm dependencies yet; SPEC-12 adds the
# pnpm install with Remotion, Chrome Headless Shell and FFmpeg. Base pinned in infra/images.env.
ARG NODE_IMAGE
FROM ${NODE_IMAGE} AS runtime
# SPEC-02 B15 deviation: runtime health server; node only (no npm/corepack).
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack \
    && rm -f /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack
WORKDIR /repo
COPY media/scenes/package.json media/scenes/
COPY media/scenes/src media/scenes/src
ARG GIT_SHA=unknown
ENV NODE_ENV=production APP_VERSION=${GIT_SHA} PORT=8002
USER node
CMD ["node", "media/scenes/src/server.ts"]
