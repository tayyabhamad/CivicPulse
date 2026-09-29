import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, rmSync } from "node:fs";
import { resolve } from "node:path";

const schemaPath = process.env.OPENAPI_SCHEMA_PATH ?? "../backend/openapi.json";
const outputPath = resolve("src/api/openapi.generated.ts");
const check = process.argv.includes("--check");

const inputPath = resolve(schemaPath);
if (!existsSync(inputPath)) {
  console.error(`OpenAPI schema not found: ${inputPath}`);
  process.exit(1);
}

const generatedPath = check ? `${outputPath}.tmp` : outputPath;
try {
  execFileSync(process.execPath, ["node_modules/openapi-typescript/bin/cli.js", inputPath, "-o", generatedPath], {
    stdio: "inherit"
  });
  if (check && readFileSync(generatedPath, "utf8") !== readFileSync(outputPath, "utf8")) {
    console.error("OpenAPI types are out of date. Run `python -m scripts.export_openapi` in backend, then `npm run generate:api` in frontend.");
    process.exitCode = 1;
  }
} finally {
  if (check && existsSync(generatedPath)) rmSync(generatedPath);
}
