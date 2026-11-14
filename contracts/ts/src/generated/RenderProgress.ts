/* eslint-disable */

export interface RenderProgress {
  scenes: {
    percent?: number;
    sceneId: string;
    status: "queued" | "rendering" | "reused" | "done" | "failed";
  }[];
}
