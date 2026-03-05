import { defineConfig } from "@playwright/test";
import path from "path";

const repoRoot = path.resolve(__dirname, "..");

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: {
    timeout: 15_000
  },
  retries: 1,
  reporter: [
    ["list"],
    ["html", { outputFolder: path.join(repoRoot, "artifacts", "playwright-report"), open: "never" }]
  ],
  use: {
    headless: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off"
  },
  outputDir: path.join(repoRoot, "artifacts", "test-results")
});
