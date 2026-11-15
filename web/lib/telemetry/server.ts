import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-http";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { UndiciInstrumentation } from "@opentelemetry/instrumentation-undici";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { NodeSDK } from "@opentelemetry/sdk-node";
import { PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import { registerServiceUp } from "./service-up";

let started = false;

export function initServerTelemetry(): void {
  if (started) return;
  started = true;
  if (process.env.OTEL_SDK_DISABLED === "true" || process.env.OTEL_SDK_DISABLED === "1") {
    return;
  }
  const endpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://otel-collector:4318";
  const resource = resourceFromAttributes({
    "service.name": "web",
    "service.version": process.env.APP_VERSION ?? "unknown",
    "deployment.environment": process.env.APP_ENV ?? "dev",
  });
  const sdk = new NodeSDK({
    resource,
    traceExporter: new OTLPTraceExporter({ url: `${endpoint}/v1/traces` }),
    metricReader: new PeriodicExportingMetricReader({
      exporter: new OTLPMetricExporter({ url: `${endpoint}/v1/metrics` }),
    }),
    instrumentations: [
      new HttpInstrumentation({
        ignoreIncomingRequestHook: (req) => {
          const url = req.url ?? "";
          return url.startsWith("/healthz") || url.startsWith("/readyz");
        },
      }),
      new UndiciInstrumentation(),
    ],
  });
  sdk.start();
  registerServiceUp();
}
