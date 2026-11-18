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

  test("T-38 rejects Content-Length above cap before reading body", async () => {
    const fetchMock = vi.mocked(globalThis.fetch);
    const { POST } = await import("../app/api/otel/[...path]/route");
    const res = await POST(
      new Request("http://web/api/otel/v1/traces", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "content-length": String(512 * 1024 + 1),
        },
        body: "small",
      }),
      { params: Promise.resolve({ path: ["v1", "traces"] }) },
    );
    expect(res.status).toBe(413);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("T-38 rejects streamed bodies above cap", async () => {
    const { POST } = await import("../app/api/otel/[...path]/route");
    const chunk = new Uint8Array(64 * 1024);
    chunk.fill(1);
    const stream = new ReadableStream<Uint8Array>({
      pull(controller) {
        for (let i = 0; i < 9; i += 1) {
          controller.enqueue(chunk);
        }
        controller.close();
      },
    });
    const res = await POST(
      new Request("http://web/api/otel/v1/traces", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: stream,
        duplex: "half",
      } as RequestInit),
      { params: Promise.resolve({ path: ["v1", "traces"] }) },
    );
    expect(res.status).toBe(413);
  });
});
