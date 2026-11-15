import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

describe("OTLP browser proxy", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(null, { status: 202 })),
    );
    process.env.OTEL_EXPORTER_OTLP_ENDPOINT = "http://otel-collector:4318";
  });

  afterEach(() => {
    vi.stubGlobal("fetch", originalFetch);
  });

  test("T-38 allows only v1/traces", async () => {
    const { POST } = await import("../app/api/otel/[...path]/route");
    const bad = await POST(
      new Request("http://web/api/otel/v1/metrics", { method: "POST", body: "x" }),
      { params: Promise.resolve({ path: ["v1", "metrics"] }) },
    );
    expect(bad.status).toBe(404);
    const good = await POST(
      new Request("http://web/api/otel/v1/traces", {
        method: "POST",
        headers: { "content-type": "application/x-protobuf" },
        body: "abc",
      }),
      { params: Promise.resolve({ path: ["v1", "traces"] }) },
    );
    expect(good.status).toBe(202);
  });

  test("T-38 rejects unsupported content types", async () => {
    const { POST } = await import("../app/api/otel/[...path]/route");
    const res = await POST(
      new Request("http://web/api/otel/v1/traces", {
        method: "POST",
        headers: { "content-type": "text/plain" },
        body: "x",
      }),
      { params: Promise.resolve({ path: ["v1", "traces"] }) },
    );
    expect(res.status).toBe(415);
  });

  test("T-38 rejects oversized bodies", async () => {
    const { POST } = await import("../app/api/otel/[...path]/route");
    const big = "x".repeat(512 * 1024 + 1);
    const res = await POST(
      new Request("http://web/api/otel/v1/traces", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: big,
      }),
      { params: Promise.resolve({ path: ["v1", "traces"] }) },
    );
    expect(res.status).toBe(413);
  });
});
