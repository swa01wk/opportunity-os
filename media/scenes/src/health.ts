// Render service health (OBSERVABILITY.md): /healthz is liveness; /readyz checks the
// object store, the only dependency render has (SPEC-01a). SPEC-12 adds the job API.
import { connect } from "node:net";

import { log } from "./telemetry/logger.ts";

export type Check = () => Promise<void>;
export type Reply = { status: number; body: Record<string, unknown> };

const TIMEOUT_MS = 2000;

export function tcpCheck(url: string): Check {
  const parsed = new URL(url);
  const port = Number(parsed.port || (parsed.protocol === "https:" ? 443 : 80));
  return () =>
    new Promise((resolve, reject) => {
      const socket = connect({ host: parsed.hostname, port, timeout: TIMEOUT_MS });
      socket.once("connect", () => {
        socket.end();
        resolve();
      });
      socket.once("timeout", () => socket.destroy(new Error("timeout")));
      socket.once("error", reject);
    });
}

export async function reply(
  path: string,
  service: string,
  version: string,
  checks: Record<string, Check>,
): Promise<Reply> {
  const base = { service, version };
  if (path === "/healthz") return { status: 200, body: { status: "ok", ...base } };
  if (path !== "/readyz") return { status: 404, body: { status: "not_found" } };
  const names = Object.keys(checks);
  const results = await Promise.allSettled(names.map((name) => checks[name]!()));
  const outcome = Object.fromEntries(
    names.map((name, i) => [name, results[i]!.status === "fulfilled" ? "ok" : "fail"]),
  );
  const ready = Object.values(outcome).every((value) => value === "ok");
  if (!ready) {
    for (const [name, status] of Object.entries(outcome)) {
      if (status === "fail") log(service, "health.not_ready", { dependency: name });
    }
  }
  return {
    status: ready ? 200 : 503,
    body: { status: ready ? "ok" : "unavailable", ...base, checks: outcome },
  };
}
