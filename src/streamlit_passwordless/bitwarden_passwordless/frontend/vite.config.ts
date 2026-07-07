import { defineConfig, UserConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    outDir: "build",
    minify: false,
    lib: {
      entry: "src/index.ts",
      name: "bitwarden-passwordless",
      formats: ["es"],
      fileName: "index",
    },
  },
}) satisfies UserConfig;
