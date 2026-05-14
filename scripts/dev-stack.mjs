#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const backendDir = path.join(root, "backend");
const frontendDir = path.join(root, "frontend");
const backendBin = path.join(backendDir, ".venv", "bin", "deadzone-backend");
const host = process.env.DEADZONE_HOST ?? "127.0.0.1";
const backendPort = process.env.DEADZONE_BACKEND_PORT ?? "8000";
const frontendPort = process.env.DEADZONE_FRONTEND_PORT ?? "3000";

const children = new Set();
let shuttingDown = false;

function log(prefix, chunk) {
  for (const line of chunk.toString().split(/\r?\n/)) {
    if (line) console.log(`[${prefix}] ${line}`);
  }
}

function start(label, command, args, cwd, env = process.env) {
  const child = spawn(command, args, { cwd, env, stdio: ["ignore", "pipe", "pipe"] });
  children.add(child);
  child.stdout.on("data", (chunk) => log(label, chunk));
  child.stderr.on("data", (chunk) => log(label, chunk));
  child.on("exit", (code, signal) => {
    children.delete(child);
    if (!shuttingDown && code !== 0) {
      console.error(`[${label}] exited with ${signal ?? code}`);
      shutdown(code ?? 1);
    }
  });
  return child;
}

function requestOk(url) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => {
      res.resume();
      resolve(res.statusCode >= 200 && res.statusCode < 500);
    });
    req.on("error", () => resolve(false));
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitFor(url, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await requestOk(url)) return true;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return false;
}

function killPid(pid) {
  try {
    process.kill(pid, "SIGTERM");
  } catch {
    // Process already exited.
  }
}

function pidsListeningOn(port) {
  const result = spawnSync("lsof", ["-tiTCP:" + port, "-sTCP:LISTEN"], {
    encoding: "utf8",
  });
  if (result.status !== 0 && !result.stdout) return [];
  return result.stdout
    .split(/\s+/)
    .map((item) => Number(item))
    .filter(Boolean);
}

function commandForPid(pid) {
  const result = spawnSync("ps", ["-p", String(pid), "-o", "command="], {
    encoding: "utf8",
  });
  return result.stdout.trim();
}

function cleanupSpawnedPort(port) {
  for (const pid of pidsListeningOn(port)) {
    const command = commandForPid(pid);
    if (command.includes(root) || command.includes("DeadZone Bluetooth")) {
      killPid(pid);
    }
  }
}

function shutdown(code = 0) {
  if (shuttingDown) return;
  shuttingDown = true;
  for (const child of children) killPid(child.pid);
  cleanupSpawnedPort(backendPort);
  cleanupSpawnedPort(frontendPort);
  setTimeout(() => process.exit(code), 300).unref();
}

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => shutdown(0));
}

const backendArgs = ["--host", host, "--port", backendPort];
if (process.env.DEADZONE_DEV_NO_MACOS_BLUETOOTH_APP === "1") {
  backendArgs.push("--no-macos-bluetooth-app");
}

console.log(`Starting DeadZone backend on http://${host}:${backendPort}`);
start("backend", backendBin, backendArgs, backendDir);

const ready = await waitFor(`http://${host}:${backendPort}/healthz`, 30000);
if (!ready) {
  console.error("Backend did not become healthy within 30 seconds.");
  shutdown(1);
} else {
  console.log(`Starting DeadZone frontend on http://${host}:${frontendPort}`);
  start("frontend", "npm", ["run", "dev", "--", "--host", host, "--port", frontendPort], frontendDir);
}
