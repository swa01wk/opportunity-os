import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test } from "vitest";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../..");

const common = JSON.parse(
  readFileSync(path.join(repoRoot, "docs/contracts/common.schema.json"), "utf8"),
);
const workflow = JSON.parse(
  readFileSync(path.join(repoRoot, "docs/contracts/events/workflow-request.schema.json"), "utf8"),
);
type CatalogCase = {
  contract: string;
  file: string;
  expectValid: boolean;
  expectedCode: string | null;
};
const catalog = JSON.parse(
  readFileSync(path.join(repoRoot, "contracts/tests/fixture_catalog.json"), "utf8"),
) as CatalogCase[];

function workflowAjv() {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  ajv.addSchema(common);
  return ajv.compile(workflow);
}

const validateWorkflow = workflowAjv();

test.each(catalog.filter((entry) => entry.contract === "events/workflow-request.schema.json"))(
  "T-33 Ajv verdict for %s",
  (entry) => {
    const payload = JSON.parse(
      readFileSync(path.join(repoRoot, "docs/contracts/examples", entry.file), "utf8"),
    );
    const ok = validateWorkflow(payload) as boolean;
    expect(ok).toBe(entry.expectValid);
  },
);

test("T-33 the TypeScript contracts package exports one type per def", () => {
  const expected = [...Object.keys(common.$defs).sort(), "WorkflowRequest"];
  const index = readFileSync(path.join(repoRoot, "contracts/ts/src/index.ts"), "utf8");
  const exported = [...index.matchAll(/export type \{ (\w+) \}/gu)].map((match) => match[1]).sort();
  expect(exported).toEqual(expected);
});
