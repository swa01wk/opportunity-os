import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-http";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { NodeSDK } from "@opentelemetry/sdk-node";
import { PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import {
  ATTR_DEPLOYMENT_ENVIRONMENT_NAME,
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from "@opentelemetry/semantic-conventions";

let started = false;

export function initServerTelemetry(): void {
  if (started) return;
  started = true;
  if (process.env.OTEL_SDK_DISABLED === "true" || process.env.OTEL_SDK_DISABLED === "1") {
    return;
  }
  const endpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://otel-collector:4318";
  const resource = resourceFromAttributes({
    [ATTR_SERVICE_NAME]: "web",
    [ATTR_SERVICE_VERSION]: process.env.APP_VERSION ?? "unknown",
    [ATTR_DEPLOYMENT_ENVIRONMENT_NAME]: process.env.APP_ENV ?? "dev",
  });
  registerInstrumentations({
    instrumentations: [
      new HttpInstrumentation({
        ignoreIncomingRequestHook: (req) => {
          const url = req.url ?? "";
          return url.startsWith("/healthz") || url.startsWith("/readyz");
        },
      }),
    ],
  });
  const sdk = new NodeSDK({
    resource,
    traceExporter: new OTLPTraceExporter({ url: `${endpoint}/v1/traces` }),
    metricReader: new PeriodicExportingMetricReader({
      exporter: new OTLPMetricExporter({ url: `${endpoint}/v1/metrics` }),
    }),
  });
  sdk.start();
}
