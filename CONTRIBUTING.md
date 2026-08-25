# Contributing to turbotokens

Thanks for helping make turbotokens better. This is a Rust workspace; no JavaScript build.

## Setup

```bash
git clone https://github.com/maxmoneycash/turbotokens.git
cd turbotokens/rust
cargo build --release --bin turbotokens --features fetch-litellm-pricing
cargo test --workspace --features fetch-litellm-pricing
```

The `fetch-litellm-pricing` feature downloads the pricing snapshot at build time. For offline or sandboxed builds, set `TURBOTOKENS_PRICING_JSON_PATH` to a local LiteLLM `model_prices_and_context_window.json`.

## Rules that keep the project fast

- **Output parity is sacred.** Any change to parsing, caching, or aggregation must keep `--json` output byte-identical. `rust/bench/warm-bench.sh` checks this automatically — run it before submitting.
- **std-only hot paths.** No async runtime, no clap, no new dependencies without a measured reason in the PR description.
- **Clippy and fmt are gates:** `cargo clippy --workspace --all-targets --features fetch-litellm-pricing` must be warning-free and `cargo fmt --check` clean.
- Benchmarks for performance claims: include `bench/warm-bench.sh` or `bench/latency-probe.sh` numbers in your PR.

## Good first contributions

Look for issues labeled [`good first issue`](https://github.com/maxmoneycash/turbotokens/labels/good%20first%20issue). Extending `turbotokens live` to another agent (see `rust/adapters/codex/src/live.rs` as the template) is a great first PR.

## Reporting bugs

Include: `turbotokens doctor` output, your OS, the command you ran, and a minimal JSONL fixture that reproduces the problem (scrub anything private — lines only need `timestamp`, `message.id`, `message.model`, `message.usage`, `requestId`).
