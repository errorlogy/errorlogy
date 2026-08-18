/**
 * Cross-platform launcher: sets PYTHONPATH to `src` and runs the venv Python.
 * Usage: node scripts/run-analytics.mjs [...uvicorn args]
 * Example: node scripts/run-analytics.mjs --reload
 */
import { spawn } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, "..");
const py =
  process.platform === "win32"
    ? join(projectRoot, ".venv", "Scripts", "python.exe")
    : join(projectRoot, ".venv", "bin", "python");

const host = process.env.ANALYTICS_HOST ?? "127.0.0.1";
const port = process.env.ANALYTICS_PORT ?? "8000";

const extra = process.argv.slice(2);
const uvicornArgs = [
  "-m",
  "uvicorn",
  "analytics.main:app",
  "--host",
  host,
  "--port",
  String(port),
  ...extra,
];

const env = {
  ...process.env,
  PYTHONPATH: join(projectRoot, "src"),
};

const child = spawn(py, uvicornArgs, {
  cwd: projectRoot,
  env,
  stdio: "inherit",
  shell: false,
});

child.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 1);
});
