# check=skip=InvalidDefaultArgInFrom
# Interim S3-compatible store (ADR-015): MinIO CE built unchanged from its final source tag
# (AGPL-3.0), because the official images were withdrawn. Local only; SPEC-05 replaces it.
ARG GOLANG_IMAGE
ARG BUSYBOX_IMAGE
FROM ${GOLANG_IMAGE} AS build
ARG MINIO_SOURCE_REF
ENV CGO_ENABLED=0 GOTOOLCHAIN=local
RUN git clone --depth 1 --branch "${MINIO_SOURCE_REF}" https://github.com/minio/minio /src \
    && cd /src && go build -trimpath -ldflags "-s -w" -o /out/minio .

FROM ${BUSYBOX_IMAGE} AS runtime
COPY --from=build /out/minio /usr/bin/minio
RUN mkdir -p /data && chown 10001:10001 /data
USER 10001
EXPOSE 9000
ENTRYPOINT ["/usr/bin/minio"]
CMD ["server", "/data", "--address", ":9000", "--console-address", ":9001"]
