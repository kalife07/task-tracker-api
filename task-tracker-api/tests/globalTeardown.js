const fs = require("fs");
const path = require("path");

const serverInfoPath = path.join(__dirname, ".test-server.json");

function killProcessTree(pid) {
  if (process.platform === "win32") {
    require("child_process").spawnSync("taskkill", ["/pid", String(pid), "/t", "/f"], {
      stdio: "ignore",
    });
    return;
  }

  try {
    process.kill(-pid, "SIGTERM");
  } catch {
    try {
      process.kill(pid, "SIGTERM");
    } catch {
      // Process already exited.
    }
  }
}

module.exports = async () => {
  if (!fs.existsSync(serverInfoPath)) {
    return;
  }

  const { pid } = JSON.parse(fs.readFileSync(serverInfoPath, "utf8"));
  killProcessTree(pid);
  fs.unlinkSync(serverInfoPath);
};
