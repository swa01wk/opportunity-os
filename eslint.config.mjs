// ESLint flat config for web, media/scenes and contracts/ts (ADR-019: ESLint with jsx-a11y).
import js from "@eslint/js";
import jsxA11y from "eslint-plugin-jsx-a11y";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["**/node_modules/**", "**/.next/**", "**/dist/**", "**/coverage/**", "docs/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx,mjs}"],
    languageOptions: { globals: { ...globals.node } },
  },
  {
    files: ["web/**/*.tsx"],
    ...jsxA11y.flatConfigs.recommended,
    languageOptions: { globals: { ...globals.browser } },
  },
);
