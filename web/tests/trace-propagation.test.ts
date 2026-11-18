import { createServer, type Server } from "node:http";

import { context, trace } from "@opentelemetry/api";
import { UndiciInstrumentation } from "@opentelemetry/instrumentation-undici";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { afterEach, describe, expect, test } from "vitest";

let server: Server | undefined;

afterEach(() => server?.close());

describe("web server trace propagation", () => {
  test("T-38 fetch from an active span carries traceparent", async () => {
    const provider = new NodeTracerProvider();
    provider.register();
    registerInstrumentations({ instrumentations: [new UndiciInstrumentation()] });
    server = createServer((req, res) => {
      res.writeHead(200, { "content-type": "text/plain" });
      res.end(req.headers.traceparent ?? "");
    }).listen(0, "127.0.0.1");
    await new Promise<void>((resolve) => server!.once("listening", resolve));
    const port = (server.address() as { port: number }).port;
    const tracer = provider.getTracer("web-test");
    const traceparent = await context.with(
      trace.setSpan(context.active(), tracer.startSpan("parent")),
      async () => {
        const expectedTraceId = trace.getActiveSpan()!.spanContext().traceId;
        const res = await fetch(`http://127.0.0.1:${port}/`);
        const received = await res.text();
        expect(received).toMatch(/^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$/);
        expect(received.split("-")[1]).toBe(expectedTraceId);
        return received;
      },
    );
    expect(traceparent).toBeTruthy();
  });
});
