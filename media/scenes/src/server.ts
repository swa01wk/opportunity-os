// Render service entry point (`node src/server.ts`, Node 24 type stripping). Private
// network only; Compose publishes no host port for it (SPEC-01a, NFR-12).
import { createServer } from "node:http";
import { reply, tcpCheck } from "./health.ts";

const service = "render";
const version = process.env.APP_VERSION ?? "unknown";
const checks = {
  objectstore: tcpCheck(process.env.OBJECTSTORE_ENDPOINT ?? "http://objectstore:9000"),
};
const port = Number(process.env.PORT ?? "8002");

const log = (event: string, fields: Record<string, unknown> = {}) =>
  console.log(
    JSON.stringify({ ts: new Date().toISOString(), level: "info", service, event, ...fields }),
  );

createServer((req, res) => {
  void reply(new URL(req.url ?? "/", "http://render").pathname, service, version, checks).then(
    ({ status, body }) => {
      res.writeHead(status, { "content-type": "application/json" });
      res.end(JSON.stringify(body));
    },
  );
}).listen(port, () => log("render.started", { port }));
