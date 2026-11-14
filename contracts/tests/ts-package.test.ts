import { expect, test } from "vitest";
import { generatedFrom } from "../ts/src/index.ts";

test("T-31 the TypeScript contracts package loads", () => {
  expect(generatedFrom).toBe("contracts/python/opportunityos_contracts");
});
