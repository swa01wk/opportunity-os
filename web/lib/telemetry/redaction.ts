const DROP_PATHS = [
  "authorization",
  "cookie",
  "password",
  "client_secret",
  "api_key",
  "access_token",
  "refresh_token",
  "req.headers.authorization",
  "req.headers.cookie",
];
const EMAIL = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
const SK_PREFIX = /\bsk-[A-Za-z0-9]{16,}\b/g;
const SIGNED_URL =
  /([?&](X-Amz-Signature|X-Amz-Credential|X-Amz-Security-Token|sig|signature|token)=[^&\s]+)/gi;
const MASK = "[redacted]";

export function redactString(value: string, enabled = true): string {
  if (!enabled) return value;
  let next = value;
  next = next.replace(EMAIL, MASK);
  next = next.replace(SK_PREFIX, MASK);
  return next.replace(SIGNED_URL, (match) => `${match.split("=")[0]}=${MASK}`);
}

export function redactRecord(
  fields: Record<string, unknown>,
  enabled = true,
): Record<string, unknown> {
  if (!enabled) return fields;
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(fields)) {
    if (DROP_PATHS.includes(key.toLowerCase())) continue;
    if (typeof value === "string") out[key] = redactString(value, enabled);
    else out[key] = value;
  }
  return out;
}

export const pinoRedactPaths = DROP_PATHS;
