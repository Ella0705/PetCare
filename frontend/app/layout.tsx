import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "PetCare AI MVP",
  description: "Multi-agent pet wellness assistant"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
