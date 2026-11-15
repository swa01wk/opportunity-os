export const runtime = "nodejs";

const MAX_BODY_BYTES = 512 * 1024;
const ALLOWED_TYPES = new Set(["application/json", "application/x-protobuf"]);

const collectorBase = () => process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://otel-collector:4318";

export async function POST(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
): Promise<Response> {
  const { path } = await context.params;
  if (path.length !== 2 || path[0] !== "v1" || path[1] !== "traces") {
    return new Response(null, { status: 404 });
  }
  const contentType = request.headers.get("content-type")?.split(";")[0]?.trim() ?? "";
  if (!ALLOWED_TYPES.has(contentType)) {
    return new Response(null, { status: 415 });
  }
  const body = await request.arrayBuffer();
  if (body.byteLength > MAX_BODY_BYTES) {
    return new Response(null, { status: 413 });
  }
  // SPEC-06 adds session checks; forward only the body and content type.
  const res = await fetch(`${collectorBase()}/${path.join("/")}`, {
    method: "POST",
    headers: { "content-type": contentType },
    body,
  });
  return new Response(await res.arrayBuffer(), { status: res.status });
}
