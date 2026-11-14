import { expect, test } from "vitest";
import type { Uuid, WorkflowRequest } from "../ts/src/index.ts";

test("T-31 the TypeScript contracts package loads", () => {
  const sample: Uuid = "00000000-0000-4000-8000-000000000052";
  const request: WorkflowRequest = {
    requestId: sample,
    workflowType: "preview",
    projectId: "00000000-0000-4000-8000-000000000010",
    requestedBy: {
      type: "member",
      id: "00000000-0000-4000-8000-000000000002",
      responsibility: "editor",
    },
    input: {},
  };
  expect(request.workflowType).toBe("preview");
});
