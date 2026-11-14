/* eslint-disable @typescript-eslint/no-unused-vars */
// ruleid: oos.javascript.dynamic-import
const mod = import("./fixture-mod");

// ok: oos.javascript.dynamic-import
import type { Marker } from "./fixture-types";

export const ok = 1;