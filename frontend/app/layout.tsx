import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../styles/globals.css";
import { RootLayoutClient } from "./layout-client";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DataSafeguard — AI Governance Platform",
  description: "Enterprise AI Governance, Compliance & Security Platform",
  viewport: "width=device-width, initial-scale=1.0",
  themeColor: "#1e40af",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <RootLayoutClient>{children}</RootLayoutClient>
      </body>
    </html>
  );
}
