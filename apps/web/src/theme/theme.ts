import type { CSSProperties } from "react";
import { theme as antdTheme, type ThemeConfig } from "antd";

import designTokens from "./design-tokens.json";

export type ThemeMode = "light" | "dark";

type CssVariableName = `--${string}`;

export type ThemeCssProperties = CSSProperties &
  Record<CssVariableName, string | number>;

const sharedAntdToken = {
  ...designTokens.borderRadius,
  ...designTokens.padding,
  ...designTokens.margin,
  fontSizeSM: designTokens.fontSize.fontSizeSM,
  fontSize: designTokens.fontSize.fontSize,
  fontSizeLG: designTokens.fontSize.fontSizeLG,
  fontSizeXL: designTokens.fontSize.fontSizeXL,
  fontSizeHeading1: designTokens.heading.heading1,
  fontSizeHeading2: designTokens.heading.heading2,
  fontSizeHeading3: designTokens.heading.heading3,
  fontSizeHeading4: designTokens.heading.heading4,
  fontSizeHeading5: designTokens.heading.heading5,
} satisfies NonNullable<ThemeConfig["token"]>;

function getColorTokens(mode: ThemeMode) {
  return mode === "dark" ? designTokens.darkToken : designTokens.lightToken;
}

export function createAntdTheme(mode: ThemeMode): ThemeConfig {
  const colors = getColorTokens(mode);

  return {
    algorithm:
      mode === "dark" ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    cssVar: { key: "feedbackos" },
    token: {
      ...sharedAntdToken,
      colorPrimaryBg: colors.colorPrimaryBg,
      colorPrimaryBorder: colors.colorPrimaryBorder,
      colorPrimary: colors.colorPrimary,
      colorPrimaryHover: colors.colorPrimaryHover,
      colorPrimaryActive: colors.colorPrimaryActive,
      colorBgBase: colors.colorBgBase,
      colorBgLayout: colors.colorBgLayout,
      colorBgContainer: colors.colorBgContainer,
      colorBgMask: colors.colorBgMask,
      colorTextBase: colors.colorTextBase,
      colorText: colors.colorText,
      colorTextSecondary: colors.colorTextSecondary,
      colorTextTertiary: colors.colorTextTertiary,
      colorTextQuaternary: colors.colorTextQuaternary,
      colorBorder: colors.colorBorder,
      colorBorderSecondary: colors.colorBorderSecondary,
      colorFill: colors.colorFill,
      colorFillSecondary: colors.colorFillSecondary,
      colorFillTertiary: colors.colorFillTertiary,
      colorFillQuaternary: colors.colorFillQuaternary,
      colorInfo: colors.colorInfo,
      colorInfoHover: colors.colorInfoHover,
      colorInfoBg: colors.colorInfoBg,
      colorInfoBorder: colors.colorInfoBorder,
      colorInfoActive: colors.colorInfoActive,
      colorSuccess: colors.colorSuccess,
      colorSuccessHover: colors.colorSuccessHover,
      colorSuccessBg: colors.colorSuccessBg,
      colorSuccessBorder: colors.colorSuccessBorder,
      colorSuccessActive: colors.colorSuccessActive,
      colorWarning: colors.colorWarning,
      colorWarningHover: colors.colorWarningHover,
      colorWarningBg: colors.colorWarningBg,
      colorWarningBorder: colors.colorWarningBorder,
      colorWarningActive: colors.colorWarningActive,
      colorError: colors.colorError,
      colorErrorHover: colors.colorErrorHover,
      colorErrorBg: colors.colorErrorBg,
      colorErrorBorder: colors.colorErrorBorder,
      colorErrorActive: colors.colorErrorActive,
      colorLink: colors.colorLink,
      colorLinkHover: colors.colorLinkHover,
      colorLinkActive: colors.colorLinkActive,
      boxShadow: colors.boxShadow,
      boxShadowSecondary: colors.boxShadowSecondary,
    },
  };
}

function toKebabCase(value: string) {
  return value.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();
}

function addTokenGroup(
  target: ThemeCssProperties,
  group: Record<string, string | number>,
) {
  for (const [name, value] of Object.entries(group)) {
    target[`--fo-${toKebabCase(name)}`] =
      typeof value === "number" ? `${value}px` : value;
  }
}

export function createCssVariables(mode: ThemeMode): ThemeCssProperties {
  const variables = { colorScheme: mode } as ThemeCssProperties;

  addTokenGroup(variables, getColorTokens(mode));
  addTokenGroup(variables, designTokens.borderRadius);
  addTokenGroup(variables, designTokens.padding);
  addTokenGroup(variables, designTokens.margin);
  addTokenGroup(variables, designTokens.fontSize);
  addTokenGroup(variables, designTokens.heading);

  return Object.assign(variables, {
    "--color-canvas": "var(--fo-color-bg-base)",
    "--color-layout": "var(--fo-color-bg-layout)",
    "--color-surface": "var(--fo-color-bg-container)",
    "--color-text": "var(--fo-color-text)",
    "--color-text-secondary": "var(--fo-color-text-secondary)",
    "--color-border": "var(--fo-color-border)",
    "--color-primary": "var(--fo-color-primary)",
    "--color-info": "var(--fo-color-info)",
    "--color-success": "var(--fo-color-success)",
    "--color-warning": "var(--fo-color-warning)",
    "--color-error": "var(--fo-color-error)",
    "--space-xs": "var(--fo-padding-xs)",
    "--space-sm": "var(--fo-padding-sm)",
    "--space-md": "var(--fo-padding)",
    "--space-lg": "var(--fo-padding-lg)",
    "--space-xl": "var(--fo-padding-xl)",
    "--radius-sm": "var(--fo-border-radius-sm)",
    "--radius-md": "var(--fo-border-radius)",
    "--radius-lg": "var(--fo-border-radius-lg)",
    "--font-size-small": "var(--fo-font-size-sm)",
    "--font-size-body": "var(--fo-font-size)",
    "--font-size-large": "var(--fo-font-size-lg)",
    "--font-size-heading-1": "var(--fo-heading1)",
    "--font-size-heading-2": "var(--fo-heading2)",
    "--font-size-heading-3": "var(--fo-heading3)",
    "--font-size-heading-4": "var(--fo-heading4)",
    "--font-size-heading-5": "var(--fo-heading5)",
    "--shadow-primary": "var(--fo-box-shadow)",
    "--shadow-secondary": "var(--fo-box-shadow-secondary)",
  });
}

export { designTokens };
