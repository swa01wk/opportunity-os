import { describe, expect, test } from "vitest";
import { healthBody } from "../lib/health";

describe("web health", () => {
  test("T-31 healthz body names the service and version", () => {
    expect(healthBody("web", "abc1234")).toEqual({
      status: "ok",
      service: "web",
      version: "abc1234",
    });
  });

  test("T-31 version falls back to unknown", () => {
    expect(healthBody("web", undefined).version).toBe("unknown");
  });
});
