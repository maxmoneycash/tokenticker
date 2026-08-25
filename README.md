# turbotokens

**Know what your AI coding agents are costing you — as it happens.**

[![ci](https://github.com/maxmoneycash/turbotokens/actions/workflows/ci.yml/badge.svg)](https://github.com/maxmoneycash/turbotokens/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/maxmoneycash/turbotokens)](https://github.com/maxmoneycash/turbotokens/releases)

Claude Code, Codex, and a dozen other agents write every token they burn into local log files. turbotokens turns those logs into a live ticker of your AI spend: a real-time dashboard, instant cost reports, budget alerts, and metrics you can pipe anywhere. A single Rust binary, no runtime to install. Reports that used to take seconds come back in milliseconds — and new usage shows up in about a tenth of a second.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/maxmoneycash/turbotokens/main/install.sh | sh
```

Prebuilt binaries for macOS (arm64/x64) and Linux (x64) are on the [Releases](https://github.com/maxmoneycash/turbotokens/releases) page. Or build from source: `cargo install --path rust/crates/turbotokens --features fetch-litellm-pricing`.

## See your spend live

```bash
turbotokens live
```

![turbotokens live dashboard: today's tokens and cost, burn-rate sparkline, model share bars, active sessions, and a stream of usage events](assets/live-dashboard.png)

A dashboard that updates the moment an agent writes a log line: today's tokens and cost, burn rate over the last 5 minutes, which models you're using, which sessions are active right now, and a stream of every usage event as it lands.

Point it at whatever you use: `turbotokens live --agent codex`.

## Turn telemetry into action

```bash
# Stream every event as JSON — pipe it anywhere
turbotokens live --json | jq -r 'select(.type=="usage") | .cost'

# Get pinged when today gets expensive
turbotokens live --alert-cost 25 --webhook https://hooks.slack.com/...

# Feed Grafana or any Prometheus setup
turbotokens live --serve 127.0.0.1:9090
```

## Reports that don't make you wait

```bash
turbotokens daily              # cost by day
turbotokens weekly             # by week
turbotokens session            # by session
turbotokens blocks             # 5-hour billing windows
turbotokens daily --watch      # auto-refresh as logs change
```

![turbotokens daily report table](assets/daily-report.png)

Want them instant, always, even while you work?

```bash
turbotokens daemon start
```

A resident process keeps your usage indexed in memory. Every report after that answers in **under a millisecond** — on gigabyte datasets, while new data is still arriving. Tools that poll your usage every few seconds stop melting your CPU.

## By the numbers

Measured on a real 2.5 GB / 1,641-file dataset, median of 10+ runs, byte-identical output ([reproduce](rust/bench)):

| | |
| --- | --- |
| Full report, cold scan (no cache) | **145 ms** |
| Same report on an unchanged dataset | **10 ms** |
| Report served by the daemon | **< 1 ms** |
| Live event latency (log write → on screen) | **p95 ≈ 110 ms** |
| Agents supported | **17** (Claude Code, Codex, OpenCode, Amp, Gemini, Copilot, Kimi, Grok Build, Qwen, and more) |

## How it compares

Same report, same 2.5 GB of logs, same machine (median of repeated runs; turbotokens cold = cache disabled, the worst case):

| | turbotokens | ccusage | claude-code-usage-monitor | Menu-bar apps (SessionWatcher, Pacer) |
| --- | --- | --- | --- | --- |
| What it is | Single Rust binary | TypeScript CLI (Node/Bun) | Python CLI | Native macOS apps |
| Full usage report | **145 ms** | 6.2–9.9 s | — | — |
| Repeat on unchanged data | **10 ms** (parse + report cache) | Re-parses every file, every run | — | — |
| Real-time event stream | ✔ ~110 ms latency | Active-block monitor only | ✔ Claude only | ✔ |
| Agents covered | **17** | ~16 | 1 | 1–2 |
| Budget alerts / webhooks | ✔ | ✗ | ✗ | Notifications only |
| Prometheus / metrics endpoint | ✔ | ✗ | ✗ | ✗ |
| Pipeable JSON everywhere | ✔ | ✔ | ✗ | ✗ |

That's **43–68x faster** than the most popular alternative on a cold scan and **600x+** on a warm one — and turbotokens is the only one that streams every agent's usage live with alerts and metrics built in.

## Zero to working

```bash
$ turbotokens doctor
✓ version: 1.0.0
✓ claude data: ~/.claude (1,084 JSONL files, 1.6 GB)
✓ codex data: ~/.codex/sessions (559 JSONL files)
✓ parse cache: 5,946 entries, 99.8 MB
✓ embedded pricing: loadable (460 models)
```

One command tells you what turbotokens sees, what's healthy, and what to fix. Shell completions included: `turbotokens completions zsh`.

## Development

```bash
cd rust
cargo build --release --bin turbotokens --features fetch-litellm-pricing
cargo test --workspace --features fetch-litellm-pricing

bench/warm-bench.sh 10     # warm-vs-uncached median + byte-parity check
bench/latency-probe.sh 20  # live-mode end-to-end latency, p50/p95
```
