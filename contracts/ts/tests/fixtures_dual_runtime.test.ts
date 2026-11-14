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
const DOMAIN_CONTRACT = "events/domain-event.schema.json";
const ANALYTICS_CONTRACT = "analytics/events.schema.json";

type FixtureCase = {
  contract: string;
  file: string;
  expectValid: boolean;
  expectedCode: string | null;
};

function sortedJsonExamples(suffix: string): string[] {
  const examplesDir = path.join(repoRoot, "docs/contracts/examples");
  return readdirSync(examplesDir)
    .filter((name) => name.endsWith(suffix))
    .sort();
}

function loadFixtureCases(): FixtureCase[] {
  const manifest = JSON.parse(
    readFileSync(path.join(repoRoot, "docs/contracts/examples/invalid/manifest.json"), "utf8"),
  ) as { fixtures: { file: string; contract: string; level: string; expected: string }[] };

  const valid: FixtureCase[] = [
    ...sortedJsonExamples(".workflow-request.json").map((file) => ({
      contract: WORKFLOW_CONTRACT,
      file,
      expectValid: true,
      expectedCode: null,
    })),
    ...sortedJsonExamples(".event.json").map((file) => ({
      contract: DOMAIN_CONTRACT,
      file,
      expectValid: true,
      expectedCode: null,
    })),
    ...sortedJsonExamples(".analytics-event.json").map((file) => ({
      contract: ANALYTICS_CONTRACT,
      file,
      expectValid: true,
      expectedCode: null,
    })),
  ];

  const registered = new Set([WORKFLOW_CONTRACT, DOMAIN_CONTRACT, ANALYTICS_CONTRACT]);
  const invalid = manifest.fixtures
    .filter((entry) => entry.level === "schema" && registered.has(entry.contract))
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
  ajv.addKeyword("x-kpis");
  ajv.addKeyword("x-agui");
  (ajvFormats as unknown as FormatsPlugin)(ajv);
  const contractsDir = path.join(repoRoot, "docs/contracts");
  for (const file of listSchemaFiles(contractsDir)) {
    ajv.addSchema(JSON.parse(readFileSync(file, "utf8")));
  }
  return ajv;
}

const ajv = buildAjv();

function validatorFor(contract: string) {
  const rel = path.join("docs/contracts", contract);
  const schema = JSON.parse(readFileSync(path.join(repoRoot, rel), "utf8"));
  const id = schema.$id as string;
  const validate = ajv.getSchema(id);
  if (validate === undefined) {
    throw new Error(`missing compiled schema for ${id}`);
  }
  return validate;
}

const catalog = loadFixtureCases();

test.each(catalog)("T-33 Ajv verdict for %s (%s)", (entry) => {
  const payload = JSON.parse(
    readFileSync(path.join(repoRoot, "docs/contracts/examples", entry.file), "utf8"),
  );
  const validate = validatorFor(entry.contract);
  const ok = validate(payload) as boolean;
  expect(ok).toBe(entry.expectValid);
});

test("T-33 the TypeScript contracts package exports generated types", () => {
  const index = readFileSync(path.join(repoRoot, "contracts/ts/src/index.ts"), "utf8");
  const exported = [...index.matchAll(/export type \{ (\w+) \}/gu)].map((match) => match[1]).sort();
  expect(exported).toContain("DomainEvent");
  expect(exported).toContain("AnalyticsEvent");
  expect(exported).toContain("WorkflowRequest");
  expect(exported.length).toBeGreaterThan(10);
});
