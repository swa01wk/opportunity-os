# check=skip=InvalidDefaultArgInFrom
# worker (DBOS from SPEC-09, ADR-003): the backend package with the agent and media/audio
# packages it imports. Bases pinned in infra/images.env.
ARG PYTHON_IMAGE
ARG UV_IMAGE
FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS runtime
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv PATH=/opt/venv/bin:$PATH PYTHONUNBUFFERED=1
WORKDIR /repo
COPY pyproject.toml uv.lock ./
COPY backend backend
COPY agent agent
COPY media/audio media/audio
COPY contracts/python contracts/python
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable --package opportunityos --extra worker
ARG GIT_SHA=unknown
ENV APP_VERSION=${GIT_SHA} PORT=8001
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
USER 10001
CMD ["python", "-m", "opportunityos.worker"]
