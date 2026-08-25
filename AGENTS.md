# AGENTS.md

turbotokens is a Rust workspace under `rust/`. There is no JavaScript build;
the binary is the product.

## Layout

- `rust/crates/turbotokens` — the CLI binary (`src/main.rs`), report runners, `blocks`
- `rust/crates/turbotokens-core` — shared types, pricing, aggregation, output
- `rust/crates/turbotokens-cli-parser` — hand-rolled CLI parser (no clap) with
  JSON-driven help codegen
- `rust/crates/turbotokens-adapter-all` — unified multi-agent report
- `rust/adapters/<agent>` — per-agent log loaders; `claude` is the largest and
  owns the parse cache (`cache.rs`), the daily fast path (`daily.rs`), and the
  real-time telemetry stream (`live.rs`)
- `rust/bench` — `warm-bench.sh` (cache speedup + parity) and
  `latency-probe.sh` (live-mode latency)

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
