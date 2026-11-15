import { describe, expect, test } from "vitest";

import { redactFields } from "../src/telemetry/redaction.ts";

describe("render logger redaction", () => {
  test("T-38 masks emails and drops authorization", () => {
    const line = redactFields({
      event: "render.started",
      authorization: "Bearer secret",
      note: "contact owner@example.com",
    });
    expect(line).not.toHaveProperty("authorization");
    expect(JSON.stringify(line)).not.toContain("owner@example.com");
  });
});
