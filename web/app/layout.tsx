import type { ReactNode } from "react";

import { TelemetryProvider } from "../components/telemetry-provider";

export const metadata = { title: "OpportunityOS Studio" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <TelemetryProvider />
        {children}
      </body>
    </html>
  );
}
