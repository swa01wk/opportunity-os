import { Writable } from "node:stream";

import pino from "pino";
import { describe, expect, test } from "vitest";

import { redactRecord, redactString } from "../lib/telemetry/redaction";

describe("web pino logger redaction", () => {
  test("T-38 masks emails in string messages", () => {
    const lines: string[] = [];
    const stream = new Writable({
      write(chunk, _enc, cb) {
        lines.push(String(chunk));
        cb();
      },
    });
    const log = pino(
      {
        formatters: { log: (obj) => redactRecord(obj as Record<string, unknown>) },
        hooks: {
          logMethod(args, method) {
            const next = args.map((arg) => (typeof arg === "string" ? redactString(arg) : arg));
            return method.apply(this, next as Parameters<typeof method>);
          },
        },
      },
      stream,
    );
    log.info("hello owner@example.com");
    expect(lines.join("")).not.toContain("owner@example.com");
  });
});
