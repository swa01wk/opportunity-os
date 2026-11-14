import { defineConfig } from "vitest/config";

// Contract tests for both runtimes live in contracts/tests/ (testing.mdc).
export default defineConfig({ test: { root: "..", include: ["tests/**/*.test.ts"] } });
