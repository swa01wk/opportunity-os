import { initServerTelemetry } from "./lib/telemetry/server";

export async function register(): Promise<void> {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    initServerTelemetry();
  }
}
