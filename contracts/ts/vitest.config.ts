import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const here = path.dirname(fileURLToPath(import.meta.url));

// Contract tests for both runtimes live in contracts/tests/ (testing.mdc).
// Vitest root is contracts/; ajv lives under contracts/ts/node_modules, so alias it here.
export default defineConfig({
  test: { root: "..", include: ["tests/**/*.test.ts", "ts/tests/**/*.test.ts"] },
  resolve: {
    alias: {
      ajv: path.join(here, "node_modules/ajv"),
      "ajv-formats": path.join(here, "node_modules/ajv-formats"),
    },
  },
});
