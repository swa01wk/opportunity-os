import { healthBody } from "../../lib/health";

export const dynamic = "force-dynamic";

export function GET(): Response {
  return Response.json(healthBody("web"));
}
