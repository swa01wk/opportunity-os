import { initServerTelemetry } from "./lib/telemetry/server";

export async function register(): Promise<void> {
  initServerTelemetry();
}
