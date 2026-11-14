/* eslint-disable */

export interface Money {
  /**
   * Amount in minor units (paise, cents).
   */
  amountMinor: number;
  currency: string;
  /**
   * Recorded conversion rate into the reporting currency (INR, Q-05), as a decimal string.
   */
  fxRateToReporting?: string;
}
