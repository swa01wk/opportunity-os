import pino from "pino";

import { pinoRedactPaths } from "./redaction";

const enabled = process.env.OOS_LOG_REDACTION !== "0";

export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  base: { service: "web" },
  timestamp: pino.stdTimeFunctions.isoTime,
  redact: enabled
    ? {
        paths: pinoRedactPaths,
        censor: "[redacted]",
      }
    : undefined,
  formatters: {
    level: (label) => ({ level: label }),
  },
});
