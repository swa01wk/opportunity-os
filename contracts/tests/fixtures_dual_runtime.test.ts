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
const preview = JSON.parse(
  readFileSync(
    path.join(repoRoot, "docs/contracts/examples/preview.workflow-request.json"),
    "utf8",
  ),
);

test("T-33 Ajv accepts the preview workflow fixture", () => {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  ajv.addSchema(common);
  const validate = ajv.compile(workflow);
  expect(validate(preview)).toBe(true);
});

test("T-33 the TypeScript contracts package exports one type per def", () => {
  const expected = [...Object.keys(common.$defs).sort(), "WorkflowRequest"];
  const index = readFileSync(path.join(repoRoot, "contracts/ts/src/index.ts"), "utf8");
  const exported = [...index.matchAll(/export type \{ (\w+) \}/gu)].map((match) => match[1]).sort();
  expect(exported).toEqual(expected);
});
