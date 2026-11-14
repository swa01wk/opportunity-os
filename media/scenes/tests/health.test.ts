import { createServer, type Server } from "node:net";
import { afterEach, describe, expect, test } from "vitest";
import { reply, tcpCheck } from "../src/health.ts";

const ok = async () => {};
const down = async () => {
  throw new Error("unreachable");
};

let server: Server | undefined;
afterEach(() => server?.close());

describe("render health", () => {
  test("T-31 healthz names the service and version", async () => {
    expect(await reply("/healthz", "render", "abc1234", { objectstore: down })).toEqual({
      status: 200,
      body: { status: "ok", service: "render", version: "abc1234" },
    });
  });

  test("T-31 readyz is 503 and names the failed dependency", async () => {
    const result = await reply("/readyz", "render", "v", { objectstore: down });
    expect(result.status).toBe(503);
    expect(result.body.checks).toEqual({ objectstore: "fail" });
  });

  test("T-31 readyz is 200 when the object store answers", async () => {
    expect((await reply("/readyz", "render", "v", { objectstore: ok })).status).toBe(200);
  });

  test("T-31 tcpCheck connects to a listening port", async () => {
    server = createServer().listen(0, "127.0.0.1");
    await new Promise((resolve) => server!.once("listening", resolve));
    const address = server.address();
    const port = typeof address === "object" && address ? address.port : 0;
    await expect(tcpCheck(`http://127.0.0.1:${port}`)()).resolves.toBeUndefined();
  });
});
