const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const request = require("supertest");

const PORT = process.env.TEST_PORT || "8765";
const BASE_URL = `http://127.0.0.1:${PORT}`;
const projectRoot = path.resolve(__dirname, "..");
const serverInfoPath = path.join(__dirname, ".test-server.json");

function resolvePythonExecutable() {
  const candidates = [
    path.join(projectRoot, "venv", "Scripts", "python.exe"),
    path.join(projectRoot, "venv", "bin", "python"),
    "python",
  ];

  for (const candidate of candidates) {
    if (candidate === "python" || fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return "python";
}

async function waitForServer(url, attempts = 40, delayMs = 250) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await request(url).get("/health");
      if (response.status === 200) {
        return;
      }
    } catch {
      // Server not ready yet.
    }

    await new Promise((resolve) => setTimeout(resolve, delayMs));
  }

  throw new Error(`API server did not become ready at ${url}`);
}

module.exports = async () => {
  const pythonExecutable = resolvePythonExecutable();
  const serverProcess = spawn(
    pythonExecutable,
    ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", PORT],
    {
      cwd: projectRoot,
      env: { ...process.env, APP_ENV: "test" },
      stdio: ["ignore", "pipe", "pipe"],
      detached: process.platform !== "win32",
    }
  );

  serverProcess.stdout.on("data", (chunk) => process.stdout.write(chunk));
  serverProcess.stderr.on("data", (chunk) => process.stderr.write(chunk));

  await waitForServer(BASE_URL);

  fs.writeFileSync(
    serverInfoPath,
    JSON.stringify({
      pid: serverProcess.pid,
      baseUrl: BASE_URL,
    })
  );

  global.__TEST_BASE_URL__ = BASE_URL;
};
