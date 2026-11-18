import pino from "pino";

import { redactRecord, redactString } from "./redaction";

export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  base: { service: "web" },
  timestamp: pino.stdTimeFunctions.isoTime,
  formatters: {
    level: (label) => ({ level: label }),
    log: (obj) => redactRecord(obj as Record<string, unknown>),
  },
  hooks: {
    logMethod(args, method) {
      const next = args.map((arg) => (typeof arg === "string" ? redactString(arg) : arg));
      return method.apply(this, next as Parameters<typeof method>);
    },
  },
});
