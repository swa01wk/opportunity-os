import { context, propagation } from "@opentelemetry/api";

export function injectTraceHeaders(headers: Record<string, string>): Record<string, string> {
  const carrier: Record<string, string> = { ...headers };
  propagation.inject(context.active(), carrier);
  return carrier;
}
