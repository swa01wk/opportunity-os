// Render service entry point (`node src/server.ts`, Node 24 type stripping). Private
// network only; Compose publishes no host port for it (SPEC-01a, NFR-12).
import { createServer } from "node:http";

import { reply, tcpCheck } from "./health.ts";
import { log } from "./telemetry/logger.ts";
import { initTelemetry } from "./telemetry/otel.ts";

const service = "render";
const version = process.env.APP_VERSION ?? "unknown";
const checks = {
  objectstore: tcpCheck(process.env.OBJECTSTORE_ENDPOINT ?? "http://objectstore:9000"),
};
const port = Number(process.env.PORT ?? "8002");

initTelemetry(service);

createServer((req, res) => {
  void reply(new URL(req.url ?? "/", "http://render").pathname, service, version, checks).then(
    ({ status, body }) => {
      res.writeHead(status, { "content-type": "application/json" });
      res.end(JSON.stringify(body));
    },
  );
}).listen(port, () => log(service, "render.started", { port }));
