# check=skip=InvalidDefaultArgInFrom
# OpenTelemetry Collector (contrib, ADR-016) plus a static busybox so Compose can run a
# health check against the health_check extension (the upstream image has no shell).
ARG OTEL_COLLECTOR_IMAGE
ARG BUSYBOX_IMAGE
FROM ${BUSYBOX_IMAGE} AS busybox
FROM ${OTEL_COLLECTOR_IMAGE} AS runtime
COPY --from=busybox /bin/busybox /bin/busybox
COPY infra/otel-collector/config.yaml /etc/otelcol-contrib/config.yaml
USER 10001
