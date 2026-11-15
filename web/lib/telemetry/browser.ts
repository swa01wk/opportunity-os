"use client";

import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { FetchInstrumentation } from "@opentelemetry/instrumentation-fetch";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { BatchSpanProcessor, WebTracerProvider } from "@opentelemetry/sdk-trace-web";

let started = false;

export function initBrowserTelemetry(): void {
  if (started || typeof window === "undefined") return;
  started = true;
  if (process.env.NEXT_PUBLIC_OTEL_DISABLED === "true") return;
  const resource = resourceFromAttributes({
    "service.name": "web-browser",
    "service.version": process.env.NEXT_PUBLIC_APP_VERSION ?? "unknown",
    "deployment.environment": process.env.NEXT_PUBLIC_APP_ENV ?? "dev",
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
