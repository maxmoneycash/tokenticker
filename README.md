# turbotokens

Real-time token and cost telemetry for AI coding agents. Single Rust binary, no runtime.

[![version](assets/badges/version.svg)](https://github.com/maxmoneycash/turbotokens/releases)
[![agents](assets/badges/agents.svg)](#comparison)
[![cold report](assets/badges/speed.svg)](#performance)
[![built with Rust](assets/badges/rust.svg)](#development)

AI coding agents write every token they use into local JSONL logs. turbotokens reads those logs in place — nothing uploaded, no config — and turns them into cost reports, a live dashboard, budget alerts, and metrics. It supports 16 agents: Claude Code, Codex, OpenCode, Amp, Gemini, Copilot, Kimi, Grok Build, Qwen, Droid, Codebuff, Hermes, Goose, Kilo, OpenClaw, and pi-agent.

**Time to count N tokens — full cost report, no cache, identical logs for all three tools:**

| Tokens counted | On disk | turbotokens | ccusage | tokscale |
| --- | --- | --- | --- | --- |
| 1B | 69 MB | **53 ms** | 489 ms | 2.96 s |
| 5B | 347 MB | **141 ms** | 673 ms | 3.41 s |
| 10B | 769 MB | **255 ms** | 927 ms | 4.20 s |
| 25B | 1.7 GB | **571 ms** | 1.66 s | 5.61 s |
| 50B | 3.4 GB | **1.22 s** | 3.20 s | 11.6 s |

All three counted byte-identical token totals at every size — same count, very different wait ([harness](rust/bench/scaling-bench.sh), median of repeated runs; tokscale cold runs include its one-time pricing download). On real log folders — thousands of small files, not six big ones — the gap is much wider: ccusage re-parses everything on every run, so a real 2.3 GB / 1,648-file folder takes it 6–8.5 s where turbotokens answers in 170 ms cold and 10 ms warm, and a 68.2B-token production pipeline scan took 14 s vs 30+ minutes.

<img src="assets/scaling-chart.png" alt="Two-panel chart. Left: bulk scaling — turbotokens 53 ms at 1B tokens to 1.2 s at 50B, ccusage 489 ms to 3.2 s, tokscale 3.0 s to 11.6 s. Right: real workloads — real 2.3 GB folder 170 ms vs 7 s, repeat run 10 ms vs 7 s, daemon <1 ms vs no equivalent, 68B-token production scan 14 s vs 30+ min" width="1100">

<img src="assets/live-dashboard.png" alt="turbotokens live dashboard — tokens, cost, burn rate, active sessions, and events streaming in real time" width="900">

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/maxmoneycash/turbotokens/main/install.sh | sh
```

Prebuilt binaries for macOS (arm64/x64) and Linux (x64) are on the [Releases](https://github.com/maxmoneycash/turbotokens/releases) page. Or build from source: `cargo install --path rust/crates/turbotokens --features fetch-litellm-pricing`.

## Usage

`turbotokens` with no arguments prints a daily cost report across every agent it detects on your machine. From there, everything is a subcommand:

| Command | What it does |
| --- | --- |
| `turbotokens daily` / `weekly` / `monthly` / `session` | Cost reports grouped by day, week, month, or session |
| `turbotokens blocks` | Usage per 5-hour billing window |
| `turbotokens claude daily` | The same reports for one agent — every agent has its own subcommand (`codex`, `opencode`, `gemini`, `grok`, …) |
| `turbotokens live` | Real-time dashboard: today's spend, 5-minute burn rate, model share, active sessions, and every event as it lands |
| `turbotokens live --agent codex` | Live dashboard for a different agent |
| `turbotokens daemon start` | Resident index process — reports answer in under a millisecond from then on |
| `turbotokens doctor` | Shows what data it sees, cache health, and pricing coverage |

Useful flags, on every report: `--json` for piping, `--since` / `--until YYYYMMDD` for date ranges, `--breakdown` for per-model costs, `--watch` to auto-refresh as logs change.

<img src="assets/daily-report.png" alt="turbotokens daily report: date, models, input/output/cache tokens, and cost in a table" width="900">

## Live dashboard

`turbotokens live` watches the log files directly — new usage hits the screen about 100 ms after the agent writes it. It's also the integration point:

```bash
# Stream every event as JSON
turbotokens live --json | jq -r 'select(.type=="usage") | .cost'

# Webhook alert when today gets expensive
turbotokens live --alert-cost 25 --webhook https://hooks.slack.com/...

# Prometheus metrics for Grafana
turbotokens live --serve 127.0.0.1:9090
```

## Performance

Measured on a real 2.3 GB / 1,648-file Claude Code dataset, median of repeated runs, byte-identical output ([reproduce](rust/bench)):

| Report | First run (no cache) | Cached |
| --- | --- | --- |
| `claude daily` | **170 ms** | **10 ms** |
| `daily` (all 16 agents) | 5.9 s | 5.4 s |
| Any report served by the daemon | **< 1 ms** | — |
| Live event latency (log write → on screen) | p95 ≈ 110 ms | — |

The parse cache covers Claude Code logs; multi-agent scans also re-read the other agents' logs, which is why the all-agent report takes longer. `turbotokens daemon start` removes that too — it holds the index in memory and answers everything in under a millisecond.

## Comparison

Same report, same 2.3 GB of Claude Code logs, same machine. turbotokens cold = cache disabled, the worst case:

| | turbotokens | ccusage |
| --- | --- | --- |
| Full cost report, first run | **170 ms** | 6–8.5 s (**34–49x** slower) |
| Same report again | **10 ms** | re-parses every file, every run |
| Codex token accuracy | matches an independent raw-log parser to 0.0001% | double-counts Codex `token_count` events (+10.16B tokens over-reported on a 68B-token dataset) |

<img src="assets/speed-chart.png" alt="Real-world timing: real 2.3 GB log folder — turbotokens 170 ms cold / 10 ms warm vs ccusage 6–8.5 s; 68.2B-token production scan — 14 s vs 30+ min" width="900">

Capabilities, broader field ([tokscale](https://github.com/junhoyeo/tokscale) and [token-monitor](https://github.com/Javis603/token-monitor) are the other substantial multi-agent tools):

| | turbotokens | tokscale | token-monitor | ccusage | claude-code-usage-monitor | Menu-bar apps |
| --- | --- | --- | --- | --- | --- | --- |
| What it is | Single Rust binary | Rust CLI + TUI | Desktop widget (JS) | TypeScript CLI | Python CLI | Native macOS apps |
| Agents covered | 16 | 45+ | 32+ | ~16 | 1 | 1–2 |
| Interactive dashboard | Live terminal TUI | Ratatui TUI | Desktop widget | No | Terminal monitor | Yes |
| Real-time event stream | Yes, ~110 ms latency | No | Yes, live widget | Active-block monitor only | Yes, Claude only | Yes |
| Budget alerts / webhooks | Yes | No | Plan-limit tracking | No | Limit warnings | Notifications only |
| Prometheus endpoint | Yes | No | No | No | No | No |
| Pipeable JSON | Yes | Yes | — | Yes | No | No |
| Resident daemon (<1 ms reports) | Yes | No | No | No | No | No |
| Your data leaves the machine | Never | Optional public leaderboards | Optional device sync | No | No | No |

tokscale is the closest peer — Rust core, the broadest agent coverage, and a social leaderboard (which means uploading your usage if you opt in). token-monitor is a different niche: an always-on desktop widget that also tracks provider plan limits. turbotokens' niche is scripted reporting and integration: the fastest cold/warm reports, a real event stream, and alerts/metrics/JSON that plug into anything.

## In production

Measured swapping turbotokens into a real accounting pipeline over **68.2B tokens** of agent logs (9 agents, 68 models):

| | ccusage | turbotokens |
| --- | --- | --- |
| Usage scan | 30+ min | **14 s** |
| Full pipeline collection | 45+ min | **2m 13s** |
| Tokens found | 67.4B | **68.2B** (+785M it missed) |

Pricing coverage mattered as much as speed: models ccusage priced at $0 — including 686M tokens of k3 and 397M of grok-4.6 — come back priced, $16.9K of previously-invisible spend on this dataset. Reported cost lands within 2.3% of list value instead of 28% short.

## Diagnostics

Real `turbotokens doctor` output on a working machine:

```bash
$ turbotokens doctor
✓ version: 1.0.0
✓ claude data: ~/.claude (1648 JSONL files, 2.3 GB)
✓ codex data: ~/.codex/sessions (2179 JSONL files)
✓ other agents: 3 other agents detected (opencode, gemini, grok)
✓ parse cache: 3307 entries, 58.5 MB
✓ embedded pricing: loadable (468 models)
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

## License

MIT — see [LICENSE](LICENSE).

turbotokens began as a fork of [ccusage](https://github.com/ccusage/ccusage)
by [@ryoppippi](https://github.com/ryoppippi), and is a substantial rewrite of
it. The original MIT copyright is preserved in `LICENSE` alongside the new
work's. ccusage appears in the comparison table above as the tool most people
are choosing between — the benchmarks there are measured, and the lineage is
this one.
