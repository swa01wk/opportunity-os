import { describe, expect, test } from "vitest";

import { redactRecord, redactString } from "../lib/telemetry/redaction";

describe("web logger redaction", () => {
  test("T-38 masks emails and signed URL query values", () => {
    const masked = redactString(
      "notify owner@example.com about https://x?X-Amz-Signature=deadbeef",
    );
    expect(masked).not.toContain("owner@example.com");
    expect(masked).not.toContain("deadbeef");
  });

  test("T-38 masks bare token keys but keeps input_tokens", () => {
    const out = redactRecord({
      token: "secret",
      input_tokens: 7,
      "gen_ai.usage.input_tokens": 123,
    });
    expect(out.token).toBe("[redacted]");
    expect(out.input_tokens).toBe(7);
    expect(out["gen_ai.usage.input_tokens"]).toBe(123);
  });

  test("T-38 drops sensitive keys from records", () => {
    const out = redactRecord({ password: "x", event: "auth.callback_failed" });
    expect(out).not.toHaveProperty("password");
    expect(out.event).toBe("auth.callback_failed");
  });
});
