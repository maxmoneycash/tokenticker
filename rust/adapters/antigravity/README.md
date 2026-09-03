# turbotokens-adapter-antigravity

The Antigravity adapter: it turns local Antigravity SQLite conversation
databases into the usage entries the reports render. It is a separate source
boundary from the Gemini CLI adapter, so unified reports preserve source
attribution.

## Owns

- `loader.rs` — database discovery, ordered reads, and identity-based deduplication.
- `parser.rs` — SQLite row handling, generator/step metadata protobuf decoding, token buckets, retries, and model naming.
- `paths.rs` — environment variables, default roots, and `.db` discovery.
- `report.rs` — the JSON and table shapes where they differ from the shared ones.

Anything that is not specific to this source belongs in `turbotokens-core` or
`turbotokens-adapter-common` instead.

## Data source

The adapter reads `.db` files below these default roots:

- `~/.gemini/antigravity/conversations/`
- `~/.gemini/antigravity-cli/conversations/`
- `~/.gemini/antigravity-ide/conversations/`
- `~/.gemini/antigravity-backup/conversations/`
- `~/.config/antigravity/conversations/`

`ANTIGRAVITY_DATA_DIR` accepts one or more comma-separated data roots. Each
root may contain a `conversations/` child or be the conversation directory
itself. Databases are opened read-only and must provide the `gen_metadata`
table. When present, the `steps` table contributes step and retry usage, and
`trajectory_metadata_blob` supplies the timestamp fallback; otherwise the
database file's mtime is used. SQLite, row-iteration, and protobuf failures
are reported instead of becoming empty or partial reports.

Usage records report input, total output, cache creation, cache read,
reasoning, and visible output tokens. Reasoning is carried as an extra
total-token bucket and priced at the model's output rate. Models come from the
recorded model label or the numeric model id, normalized to LiteLLM-style
names; Google provider records also try the `google/`, `gemini/`,
`vertex_ai/`, and `openrouter/google/` pricing prefixes. Retries and duplicate
copies of the same conversation are deduplicated by response, provider, and
message identities, keeping the max token counts.

## Public surface

- `loader::load_entries`
- `report::summarize_entries`
- `run`

## Depends on

- `turbotokens-adapter-common`
- `turbotokens-core`
- `jiff`
- `serde_json`
- `sqlite`

## Build layer

Built in the `adapters` Crane artifact layer; the layer compiles all adapters in one Cargo invocation, so they build concurrently.
