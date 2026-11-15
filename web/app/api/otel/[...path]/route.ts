import { NextRequest } from "next/server";

export const runtime = "nodejs";

const collectorBase = () => process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://otel-collector:4318";

async function forward(request: NextRequest, path: string[]): Promise<Response> {
  const target = `${collectorBase()}/${path.join("/")}`;
  const res = await fetch(target, {
    method: request.method,
    headers: {
      "content-type": request.headers.get("content-type") ?? "application/x-protobuf",
    },
    body: request.method === "POST" ? await request.arrayBuffer() : undefined,
  });
  return new Response(await res.arrayBuffer(), { status: res.status });
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
): Promise<Response> {
  const { path } = await context.params;
  return forward(request, path);
}
