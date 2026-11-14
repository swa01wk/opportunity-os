# check=skip=InvalidDefaultArgInFrom
# web (Next.js Studio, ADR-005). Targets: `dev` (Node and pnpm, used by the ts-tools
# service for make lint/test) and `runtime` (default, standalone output). Base in infra/images.env.
ARG NODE_IMAGE
FROM ${NODE_IMAGE} AS dev
ENV PNPM_HOME=/pnpm PATH=/pnpm:$PATH npm_config_store_dir=/pnpm/store \
    NEXT_TELEMETRY_DISABLED=1 COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable
WORKDIR /repo
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
RUN corepack install

FROM dev AS build
COPY tsconfig.base.json ./
COPY web/package.json web/
COPY media/scenes/package.json media/scenes/
COPY contracts/ts/package.json contracts/ts/
RUN --mount=type=cache,target=/pnpm/store pnpm install --frozen-lockfile
COPY web web
RUN pnpm --filter @oos/web build

FROM ${NODE_IMAGE} AS runtime
ARG GIT_SHA=unknown
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 APP_VERSION=${GIT_SHA} PORT=3000 HOSTNAME=0.0.0.0
WORKDIR /app
COPY --from=build --chown=node:node /repo/web/.next/standalone ./
COPY --from=build --chown=node:node /repo/web/.next/static ./web/.next/static
USER node
EXPOSE 3000
CMD ["node", "web/server.js"]
