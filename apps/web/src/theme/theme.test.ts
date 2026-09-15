import { theme as antdTheme } from "antd";
import { describe, expect, it } from "vitest";

import {
  createAntdTheme,
  createCssVariables,
  designTokens,
} from "./theme";

describe("FeedbackOS theme mapping", () => {
  it("maps the authoritative light tokens into Ant Design", () => {
    const theme = createAntdTheme("light");

    expect(theme.algorithm).toBe(antdTheme.defaultAlgorithm);
    expect(theme.token).toMatchObject({
      colorPrimary: designTokens.lightToken.colorPrimary,
      colorBgBase: designTokens.lightToken.colorBgBase,
      colorText: designTokens.lightToken.colorText,
      colorBorder: designTokens.lightToken.colorBorder,
      borderRadius: designTokens.borderRadius.borderRadius,
      padding: designTokens.padding.padding,
      fontSize: designTokens.fontSize.fontSize,
      fontSizeHeading1: designTokens.heading.heading1,
    });
  });

  it("maps the authoritative dark tokens into Ant Design", () => {
    const theme = createAntdTheme("dark");

    expect(theme.algorithm).toBe(antdTheme.darkAlgorithm);
    expect(theme.token).toMatchObject({
      colorPrimary: designTokens.darkToken.colorPrimary,
      colorBgBase: designTokens.darkToken.colorBgBase,
      colorText: designTokens.darkToken.colorText,
      colorBorder: designTokens.darkToken.colorBorder,
      colorWarning: designTokens.darkToken.colorWarning,
      borderRadius: designTokens.borderRadius.borderRadius,
      padding: designTokens.padding.padding,
      fontSize: designTokens.fontSize.fontSize,
      fontSizeHeading1: designTokens.heading.heading1,
    });
  });

  it("exposes design-system extensions and semantic Tailwind-ready variables", () => {
    const lightVariables = createCssVariables("light");
    const darkVariables = createCssVariables("dark");

    expect(lightVariables).toMatchObject({
      colorScheme: "light",
      "--fo-color-secondary-border":
        designTokens.lightToken.colorSecondaryBorder,
      "--fo-color-border-tertiary":
        designTokens.lightToken.colorBorderTertiary,
      "--fo-font-size-s": `${designTokens.fontSize.fontSizeS}px`,
      "--color-canvas": "var(--fo-color-bg-base)",
      "--space-md": "var(--fo-padding)",
      "--radius-md": "var(--fo-border-radius)",
      "--font-size-body": "var(--fo-font-size)",
    });
    expect(darkVariables).toMatchObject({
      colorScheme: "dark",
      "--fo-color-bg-base": designTokens.darkToken.colorBgBase,
      "--fo-color-text": designTokens.darkToken.colorText,
      "--color-canvas": "var(--fo-color-bg-base)",
    });
  });
});
