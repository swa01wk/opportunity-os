/* eslint-disable */

export type Uuid = string;
/**
 * Lowercase hex SHA-256 of canonical JSON (RFC 8785) or of file bytes.
 */
export type Sha256 = string;

/**
 * Pointer to one immutable version of a record. Approvals and manifests bind to these.
 */
export interface VersionRef {
  id: Uuid;
  sha256: Sha256;
  version: number;
}
