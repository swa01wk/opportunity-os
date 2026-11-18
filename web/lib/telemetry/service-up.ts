import { metrics, type ObservableResult } from "@opentelemetry/api";

let registered = false;

export function registerServiceUp(): void {
  if (registered) return;
  registered = true;
  const meter = metrics.getMeter("opportunityos.service");
  const gauge = meter.createObservableGauge("oos.service.up", {
    description: "Set to 1 while the process exports OTLP metrics",
  });
  gauge.addCallback((result: ObservableResult) => {
    result.observe(1);
  });
}
