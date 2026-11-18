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
ARG NEXT_PUBLIC_APP_ENV=dev
ARG NEXT_PUBLIC_APP_VERSION=unknown
ARG NEXT_PUBLIC_OTEL_DISABLED=0
ENV NEXT_PUBLIC_APP_ENV=${NEXT_PUBLIC_APP_ENV} \
    NEXT_PUBLIC_APP_VERSION=${NEXT_PUBLIC_APP_VERSION} \
    NEXT_PUBLIC_OTEL_DISABLED=${NEXT_PUBLIC_OTEL_DISABLED}
RUN --mount=type=cache,target=/pnpm/store pnpm install --frozen-lockfile
COPY web web
RUN pnpm --filter @oos/web build

FROM ${NODE_IMAGE} AS runtime
# SPEC-02 B15 deviation: runtime serves standalone output; node only (no npm/corepack).
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack \
    && rm -f /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack
ARG GIT_SHA=unknown
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 APP_VERSION=${GIT_SHA} PORT=3000 HOSTNAME=0.0.0.0
WORKDIR /app
COPY --from=build --chown=node:node /repo/web/.next/standalone ./
COPY --from=build --chown=node:node /repo/web/.next/static ./web/.next/static
USER node
EXPOSE 3000
CMD ["node", "web/server.js"]
