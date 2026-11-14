import path from "node:path";
import type { NextConfig } from "next";

// Standalone output for the web image (docker/web.Dockerfile); tracing from the workspace root
// (next runs with web/ as its working directory).
const config: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: path.resolve(process.cwd(), ".."),
  poweredByHeader: false,
};

export default config;
