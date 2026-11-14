/* eslint-disable @typescript-eslint/no-unused-vars */
// ok: oos.javascript.import.browser-automation (allowed under e2e/)
import { chromium } from "playwright";
import { test } from "playwright/test";

export const allowlisted = { chromium, test };