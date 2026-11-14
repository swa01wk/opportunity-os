# check=skip=InvalidDefaultArgInFrom
# api (FastAPI, ADR-004). Targets: `dev` (all workspace packages and dev tools, used by
# the py-tools service for make lint/test) and `runtime` (default). Bases pinned in infra/images.env.
ARG PYTHON_IMAGE
ARG UV_IMAGE
FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS base
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv PATH=/opt/venv/bin:$PATH PYTHONUNBUFFERED=1
WORKDIR /repo
COPY pyproject.toml uv.lock ./
COPY backend backend
COPY agent agent
COPY media/audio media/audio
COPY contracts/python contracts/python

FROM base AS dev
RUN apt-get update && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --all-packages

FROM base AS runtime
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable --package opportunityos
ARG GIT_SHA=unknown
ENV APP_VERSION=${GIT_SHA} PORT=8000
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
USER 10001
EXPOSE 8000
CMD ["python", "-m", "opportunityos.api.main"]
