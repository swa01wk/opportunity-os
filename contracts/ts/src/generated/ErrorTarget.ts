/* eslint-disable */

export type Uuid = string;
/**
 * Stable, human-readable ID unique within its document (objects, elements, scenes, beats, phrases).
 */
export type LocalId = string;

export interface ErrorTarget {
  accountLabel?: string;
  assetId?: Uuid;
  claimId?: Uuid;
  /**
   * JSON pointer into the failing document.
   */
  field?: string;
  objectId?: LocalId;
  sceneId?: LocalId;
}
