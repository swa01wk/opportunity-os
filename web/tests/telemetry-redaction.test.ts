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

  test("T-38 drops sensitive keys from records", () => {
    const out = redactRecord({ password: "x", event: "auth.callback_failed" });
    expect(out).not.toHaveProperty("password");
    expect(out.event).toBe("auth.callback_failed");
  });
});
