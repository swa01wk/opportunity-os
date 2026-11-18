"use client";

import { useEffect } from "react";

import { initBrowserTelemetry } from "../lib/telemetry/browser";

export function TelemetryProvider(): null {
  useEffect(() => {
    initBrowserTelemetry();
  }, []);
  return null;
}
