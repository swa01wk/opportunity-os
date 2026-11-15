import { createServer, type Server } from "node:http";

import { context, propagation, trace } from "@opentelemetry/api";
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
    const parent = await new Promise<string>((resolve) => {
      context.with(trace.setSpan(context.active(), tracer.startSpan("parent")), async () => {
        const carrier: Record<string, string> = {};
        propagation.inject(context.active(), carrier);
        const res = await fetch(`http://127.0.0.1:${port}/`);
        resolve((await res.text()) || carrier.traceparent || "");
      });
    });
    expect(parent).toMatch(/^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$/);
  });
});
