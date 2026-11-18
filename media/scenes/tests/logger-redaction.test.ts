import { Writable } from "node:stream";

import pino from "pino";
import { describe, expect, test } from "vitest";

import { redactRecord, redactString } from "../src/telemetry/redaction.ts";

describe("render pino logger", () => {
  test("T-38 redacts authorization in log output", () => {
    const lines: string[] = [];
    const stream = new Writable({
      write(chunk, _enc, cb) {
        lines.push(String(chunk));
        cb();
      },
    });
    const log = pino(
      {
        formatters: {
          log: (obj) => redactRecord(obj as Record<string, unknown>),
        },
        hooks: {
          logMethod(args, method) {
            const next = args.map((arg) => (typeof arg === "string" ? redactString(arg) : arg));
            return method.apply(this, next as [string]);
          },
        },
      },
      stream,
    );
    log.info({ authorization: "Bearer secret", event: "render.started" });
    const text = lines.join("");
    expect(text).not.toContain("Bearer secret");
    expect(text).not.toContain('"authorization"');
  });
});
