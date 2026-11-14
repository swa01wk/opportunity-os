import type { FormatsPlugin } from "ajv-formats";
import { Ajv2020 } from "ajv/dist/2020.js";
import ajvFormats from "ajv-formats";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test } from "vitest";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../..");

const WORKFLOW_CONTRACT = "events/workflow-request.schema.json";

type FixtureCase = {
  contract: string;
  file: string;
  expectValid: boolean;
  expectedCode: string | null;
};

function workflowValidExamples(): string[] {
  const examplesDir = path.join(repoRoot, "docs/contracts/examples");
  return readdirSync(examplesDir)
    .filter((name) => name.endsWith(".workflow-request.json"))
    .sort();
}

function loadFixtureCases(): FixtureCase[] {
  const manifest = JSON.parse(
    readFileSync(path.join(repoRoot, "docs/contracts/examples/invalid/manifest.json"), "utf8"),
  ) as { fixtures: { file: string; contract: string; level: string; expected: string }[] };

  const valid: FixtureCase[] = workflowValidExamples().map((file) => ({
    contract: WORKFLOW_CONTRACT,
    file,
    expectValid: true,
    expectedCode: null,
  }));

  const invalid = manifest.fixtures
    .filter((entry) => entry.level === "schema" && entry.contract === WORKFLOW_CONTRACT)
    .map((entry) => ({
      contract: entry.contract,
      file: `invalid/${entry.file}`,
      expectValid: false,
      expectedCode: entry.expected,
    }));

  return [...valid, ...invalid];
}

function listSchemaFiles(dir: string): string[] {
  const out: string[] = [];
  for (const ent of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      out.push(...listSchemaFiles(full));
    } else if (ent.name.endsWith(".schema.json")) {
      out.push(full);
    }
  }
  return out.sort();
}

function buildAjv() {
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  ajv.addKeyword("x-version");
  (ajvFormats as unknown as FormatsPlugin)(ajv);
  const contractsDir = path.join(repoRoot, "docs/contracts");
  for (const file of listSchemaFiles(contractsDir)) {
    ajv.addSchema(JSON.parse(readFileSync(file, "utf8")));
  }
  return ajv;
}

const common = JSON.parse(
  readFileSync(path.join(repoRoot, "docs/contracts/common.schema.json"), "utf8"),
);
const workflow = JSON.parse(
  readFileSync(path.join(repoRoot, "docs/contracts/events/workflow-request.schema.json"), "utf8"),
);

const ajv = buildAjv();
const workflowId = workflow.$id as string;
const validateWorkflow = ajv.getSchema(workflowId);
if (validateWorkflow === undefined) {
  throw new Error(`missing compiled schema for ${workflowId}`);
}

const catalog = loadFixtureCases();

test.each(catalog.filter((entry) => entry.contract === WORKFLOW_CONTRACT))(
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
