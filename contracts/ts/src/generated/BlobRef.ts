/* eslint-disable */

/**
 * Lowercase hex SHA-256 of canonical JSON (RFC 8785) or of file bytes.
 */
export type Sha256 = string;

/**
 * Content-addressed object in private storage (ADR-007).
 */
export interface BlobRef {
  bytes: number;
  key: string;
  mediaType: string;
  sha256: Sha256;
}
