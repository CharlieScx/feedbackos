import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppThemeProvider } from "@/theme/theme-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: "FeedbackOS",
  description: "Evidence-backed feedback decisions for product teams",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>
        <AppThemeProvider>{children}</AppThemeProvider>
      </body>
    </html>
  );
}
