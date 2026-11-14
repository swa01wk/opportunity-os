/* eslint-disable @typescript-eslint/no-unused-vars */
// ruleid: oos.javascript.new-function
const fn = new Function("return 1");

// ok: oos.javascript.new-function
const two = 1 + 1;

export const ok = two;