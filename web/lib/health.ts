// Liveness body shared by /healthz and /readyz (OBSERVABILITY.md). The Studio has no
// dependency to check yet: it reaches the API through route handlers (SPEC-07).
export type HealthBody = { status: "ok"; service: string; version: string };

export function healthBody(service: string, version = process.env.APP_VERSION): HealthBody {
  return { status: "ok", service, version: version ?? "unknown" };
}
