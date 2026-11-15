"use client";

import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { FetchInstrumentation } from "@opentelemetry/instrumentation-fetch";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { BatchSpanProcessor, WebTracerProvider } from "@opentelemetry/sdk-trace-web";
import {
  ATTR_DEPLOYMENT_ENVIRONMENT_NAME,
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from "@opentelemetry/semantic-conventions";

let started = false;

export function initBrowserTelemetry(): void {
  if (started || typeof window === "undefined") return;
  started = true;
  if (process.env.NEXT_PUBLIC_OTEL_DISABLED === "true") return;
  const resource = resourceFromAttributes({
    [ATTR_SERVICE_NAME]: "web-browser",
    [ATTR_SERVICE_VERSION]: process.env.NEXT_PUBLIC_APP_VERSION ?? "unknown",
    [ATTR_DEPLOYMENT_ENVIRONMENT_NAME]: process.env.NEXT_PUBLIC_APP_ENV ?? "dev",
  });
  const provider = new WebTracerProvider({
    resource,
    spanProcessors: [new BatchSpanProcessor(new OTLPTraceExporter({ url: "/api/otel/v1/traces" }))],
  });
  provider.register();
  registerInstrumentations({
    instrumentations: [
      new FetchInstrumentation({
        propagateTraceHeaderCorsUrls: [window.location.origin],
      }),
    ],
  });
}
