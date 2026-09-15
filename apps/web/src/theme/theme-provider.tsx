"use client";

import { ConfigProvider } from "antd";
import { useMemo, useSyncExternalStore, type ReactNode } from "react";

import {
  createAntdTheme,
  createCssVariables,
  type ThemeMode,
} from "./theme";

const darkModeQuery = "(prefers-color-scheme: dark)";

function subscribeToThemeChange(onStoreChange: () => void) {
  const mediaQuery = window.matchMedia(darkModeQuery);
  mediaQuery.addEventListener("change", onStoreChange);

  return () => mediaQuery.removeEventListener("change", onStoreChange);
}

function getThemeSnapshot(): ThemeMode {
  return window.matchMedia(darkModeQuery).matches ? "dark" : "light";
}

function getServerThemeSnapshot(): ThemeMode {
  return "light";
}

export function AppThemeProvider({ children }: Readonly<{ children: ReactNode }>) {
  const mode = useSyncExternalStore(
    subscribeToThemeChange,
    getThemeSnapshot,
    getServerThemeSnapshot,
  );
  const theme = useMemo(() => createAntdTheme(mode), [mode]);
  const cssVariables = useMemo(() => createCssVariables(mode), [mode]);

  return (
    <ConfigProvider theme={theme}>
      <div className="theme-root" data-theme={mode} style={cssVariables}>
        {children}
      </div>
    </ConfigProvider>
  );
}
