# AGENTS.md

turbotokens is a Rust workspace under `rust/`. The binary is the product;
`npm/` is only a thin downloader wrapper around release binaries.

## Layout

- `rust/crates/turbotokens` — the CLI binary (`src/main.rs`), report runners, `blocks`
- `rust/crates/turbotokens-core` — shared types, pricing, aggregation, output
- `rust/crates/turbotokens-cli-parser` — hand-rolled CLI parser (no clap) with
  JSON-driven help codegen
- `rust/crates/turbotokens-adapter-all` — unified multi-agent report
- `rust/adapters/<agent>` — per-agent log loaders; `claude` is the largest and
  owns the parse cache (`cache.rs`), the daily fast path (`daily.rs`), and the
  real-time telemetry stream (`live.rs`)
- `rust/bench` — `warm-bench.sh` (cache speedup + parity),
  `latency-probe.sh` (live-mode latency), and the token-scaling benchmark:
  `gen_scaling_data.py` (synthetic Claude-format datasets, 1B-50B tokens),
  `scaling-bench.sh` (turbotokens vs ccusage timing + parity check),
  `plot_scaling.py` (matplotlib chart)
- `npm/` — npm wrapper package (`npx turbotokens`): postinstall downloads the
  matching GitHub release binary
- `packaging/` — Homebrew formula template + publishing docs for external
  install channels (brew tap, npm, Scoop)

## Commands

```bash
cd rust
cargo build --release --bin turbotokens --features fetch-litellm-pricing
cargo test --workspace --features fetch-litellm-pricing
cargo clippy --release --bin turbotokens --features fetch-litellm-pricing
```

The pricing snapshot is embedded at build time; the `fetch-litellm-pricing`
feature downloads it, or point `TURBOTOKENS_PRICING_JSON_PATH` at a local
`model_prices_and_context_window.json`.

## Rules

- std-only on the hot paths: no async runtime, no clap, no new dependencies
  without a measured reason
- The binary version lives in `rust/Cargo.toml` (`[workspace.package]`) only
- Report output is a compatibility contract: any change to parsing or caching
  must keep `--json` output byte-identical (`rust/bench/warm-bench.sh` checks)
