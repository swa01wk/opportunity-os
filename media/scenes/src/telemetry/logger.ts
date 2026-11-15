import { redactFields } from "./redaction.ts";

const enabled = () => process.env.OOS_LOG_REDACTION !== "0";

export type LogFields = Record<string, unknown>;

export function log(service: string, event: string, fields: LogFields = {}): void {
  const line = redactFields(
    {
      ts: new Date().toISOString(),
      level: "info",
      service,
      event,
      ...fields,
    },
    enabled(),
  );
  console.log(JSON.stringify(line));
}
