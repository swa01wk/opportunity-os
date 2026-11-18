export const runtime = "nodejs";

const MAX_BODY_BYTES = 512 * 1024;
const ALLOWED_TYPES = new Set(["application/json", "application/x-protobuf"]);

const collectorBase = () => process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://otel-collector:4318";

async function readBodyWithLimit(request: Request): Promise<ArrayBuffer | Response> {
  const contentLength = request.headers.get("content-length");
  if (contentLength !== null) {
    const parsed = Number.parseInt(contentLength, 10);
    if (Number.isFinite(parsed) && parsed > MAX_BODY_BYTES) {
      return new Response(null, { status: 413 });
    }
  }
  const stream = request.body;
  if (!stream) {
    return new ArrayBuffer(0);
  }
  const reader = stream.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    total += value.byteLength;
    if (total > MAX_BODY_BYTES) {
      await reader.cancel();
      return new Response(null, { status: 413 });
    }
    chunks.push(value);
  }
  const body = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return body.buffer;
}

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
  const bodyOrResponse = await readBodyWithLimit(request);
  if (bodyOrResponse instanceof Response) {
    return bodyOrResponse;
  }
  // SPEC-06 adds session checks; forward only the body and content type.
  const res = await fetch(`${collectorBase()}/${path.join("/")}`, {
    method: "POST",
    headers: { "content-type": contentType },
    body: bodyOrResponse,
  });
  return new Response(await res.arrayBuffer(), { status: res.status });
}
