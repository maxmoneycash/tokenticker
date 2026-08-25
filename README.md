# turbotokens

Real-time token and cost telemetry for AI coding agents — Claude Code, Codex, and 15 more. Single Rust binary, no runtime.

[![ci](https://github.com/maxmoneycash/turbotokens/actions/workflows/ci.yml/badge.svg)](https://github.com/maxmoneycash/turbotokens/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/maxmoneycash/turbotokens)](https://github.com/maxmoneycash/turbotokens/releases)

turbotokens reads the log files your agents already write and turns them into a live dashboard, cost reports, budget alerts, and a metrics endpoint. A full report over 2.5 GB of logs takes 145 ms; a live event reaches the screen in about 100 ms.

<img src="assets/live-demo.gif" alt="turbotokens live dashboard — tokens, cost, burn rate, active sessions, and events streaming in real time" width="900">

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/maxmoneycash/turbotokens/main/install.sh | sh
```

Prebuilt binaries for macOS (arm64/x64) and Linux (x64) are on the [Releases](https://github.com/maxmoneycash/turbotokens/releases) page. Or build from source: `cargo install --path rust/crates/turbotokens --features fetch-litellm-pricing`.

## Live dashboard

```bash
turbotokens live                    # Claude Code
turbotokens live --agent codex      # or Codex
```

Today's tokens and cost, burn rate over the last 5 minutes, model share, active sessions, and every usage event as it lands. Not a poller: a stream.

## Reports

```bash
turbotokens daily              # cost by day
turbotokens weekly             # by week
turbotokens session            # by session
turbotokens blocks             # 5-hour billing windows
turbotokens daily --watch      # auto-refresh as logs change
```

![turbotokens daily report: date, models, input/output/cache tokens, and cost in a table](assets/daily-report.png)

`turbotokens daemon start` runs a resident process that keeps your usage indexed in memory. Reports then answer in under a millisecond, on gigabyte datasets, while new data is still arriving — and tools that poll your usage stop melting your CPU.

## Alerts, JSON, metrics

```bash
# Stream every event as JSON — pipe it anywhere
turbotokens live --json | jq -r 'select(.type=="usage") | .cost'

# Get pinged when today gets expensive
turbotokens live --alert-cost 25 --webhook https://hooks.slack.com/...

# Feed Grafana or any Prometheus setup
turbotokens live --serve 127.0.0.1:9090
```

## Performance

Measured on a real 2.5 GB / 1,641-file dataset, median of 10+ runs, byte-identical output ([reproduce](rust/bench)):

| | |
| --- | --- |
| Full report, cold scan (no cache) | **145 ms** |
| Same report on an unchanged dataset | **10 ms** |
| Report served by the daemon | **< 1 ms** |
| Live event latency (log write → on screen) | **p95 ≈ 110 ms** |
| Agents supported | **17** |

## Comparison

Same report, same 2.5 GB of logs, same machine (median of repeated runs; turbotokens cold = cache disabled, the worst case):

| | turbotokens | ccusage | claude-code-usage-monitor | Menu-bar apps (SessionWatcher, Pacer) |
| --- | --- | --- | --- | --- |
| What it is | Single Rust binary | TypeScript CLI (Node/Bun) | Python CLI | Native macOS apps |
| Full usage report | **145 ms** | 6.2–9.9 s | — | — |
| Repeat on unchanged data | **10 ms** (parse + report cache) | Re-parses every file, every run | — | — |
| Real-time event stream | Yes, ~110 ms latency | Active-block monitor only | Yes, Claude only | Yes |
| Agents covered | **17** | ~16 | 1 | 1–2 |
| Budget alerts / webhooks | Yes | No | No | Notifications only |
| Prometheus / metrics endpoint | Yes | No | No | No |
| Pipeable JSON everywhere | Yes | Yes | No | No |

That's **43–68x faster** than the most popular alternative on a cold scan and **600x+** on a warm one — and turbotokens is the only one that streams every agent's usage live with alerts and metrics built in.

## Diagnostics

```bash
$ turbotokens doctor
✓ version: 1.0.0
✓ claude data: ~/.claude (1,084 JSONL files, 2.1 GB)
✓ codex data: ~/.codex/sessions (557 JSONL files, 0.4 GB)
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
