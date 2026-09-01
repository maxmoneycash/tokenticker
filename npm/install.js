#!/usr/bin/env node
// postinstall: download the turbotokens release binary for this platform.
// Picks the GitHub release asset matching os/arch, extracts it into bin/.
"use strict";

const { execFileSync } = require("child_process");
const fs = require("fs");
const https = require("https");
const os = require("os");
const path = require("path");

const pkg = require("./package.json");
const REPO = "maxmoneycash/turbotokens";

const ASSETS = {
  "darwin-arm64": `turbotokens-macos-arm64.tar.gz`,
  "darwin-x64": `turbotokens-macos-x64.tar.gz`,
  "linux-x64": `turbotokens-linux-x64.tar.gz`,
  "win32-x64": `turbotokens-windows-x64.zip`,
};

function fail(msg) {
  console.error(`turbotokens: ${msg}`);
  process.exit(1);
}

const key = `${process.platform}-${process.arch}`;
const asset = ASSETS[key];
if (!asset) fail(`no prebuilt binary for ${key} — install from source: https://github.com/${REPO}`);

const url = `https://github.com/${REPO}/releases/download/v${pkg.version}/${asset}`;
const binDir = path.join(__dirname, "bin");
fs.mkdirSync(binDir, { recursive: true });
const archive = path.join(os.tmpdir(), asset);

console.log(`turbotokens: downloading ${url}`);
https
  .get(url, (res) => {
    if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
      https.get(res.headers.location, handle).on("error", (e) => fail(e.message));
      return;
    }
    handle(res);
  })
  .on("error", (e) => fail(e.message));

function handle(res) {
  if (res.statusCode !== 200) fail(`download failed: HTTP ${res.statusCode}`);
  const out = fs.createWriteStream(archive);
  res.pipe(out);
  out.on("finish", () => {
    out.close(() => {
      try {
        if (asset.endsWith(".zip")) {
          // bsdtar ships with Windows 10+ and handles zip fine.
          execFileSync("tar", ["-xf", archive, "-C", binDir, "turbotokens.exe"], {
            stdio: "inherit",
          });
        } else {
          execFileSync("tar", ["-xzf", archive, "-C", binDir, "turbotokens"], {
            stdio: "inherit",
          });
          fs.chmodSync(path.join(binDir, "turbotokens"), 0o755);
        }
      } catch (e) {
        fail(`extract failed: ${e.message}`);
      } finally {
        fs.rmSync(archive, { force: true });
      }
      console.log("turbotokens: installed to " + binDir);
    });
  });
}
