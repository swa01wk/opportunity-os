const DROP_KEY =
  /^(authorization|cookie|set-cookie|password|client_secret|api_key|access_token|refresh_token|id_token)$/i;
const SECRET_KEY = /secret|token|password|api[_-]?key|credential/i;
const EMAIL = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
const SK_PREFIX = /\bsk-[A-Za-z0-9]{16,}\b/g;
const SIGNED_URL =
  /([?&](X-Amz-Signature|X-Amz-Credential|X-Amz-Security-Token|sig|signature|token)=[^&\s]+)/gi;
const MASK = "[redacted]";

export function redactValue(key: string, value: unknown, enabled = true): unknown {
  if (!enabled) return value;
  if (DROP_KEY.test(key) || SECRET_KEY.test(key)) return MASK;
  if (typeof value === "string") {
    let next = value;
    if (EMAIL.test(next)) next = next.replace(EMAIL, MASK);
    if (SK_PREFIX.test(next)) next = next.replace(SK_PREFIX, MASK);
    next = next.replace(SIGNED_URL, (match) => `${match.split("=")[0]}=${MASK}`);
    return next;
  }
  if (value && typeof value === "object" && !Array.isArray(value)) {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      if (DROP_KEY.test(k)) continue;
      out[k] = redactValue(k, v, enabled);
    }
    return out;
  }
  if (Array.isArray(value)) return value.map((item) => redactValue(key, item, enabled));
  return value;
}

export function redactFields(
  fields: Record<string, unknown>,
  enabled = true,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(fields)) {
    if (DROP_KEY.test(key)) continue;
    out[key] = redactValue(key, value, enabled);
  }
  return out;
}
