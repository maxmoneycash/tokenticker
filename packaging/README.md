# Packaging

Install channels beyond `install.sh` / direct downloads.

## npm — `npx turbotokens`

`npm/` is a self-contained wrapper package: its postinstall downloads the
matching release binary from GitHub Releases.

Publishing (needs npm credentials):

```bash
cd npm
# version in package.json must equal the release tag it downloads
npm publish
```

First time also: `npm adduser`, and check the `turbotokens` name is yours
(`npm view turbotokens` — register it before someone else does).

## Homebrew — `brew install turbotokens`

Formulas live in a tap repo, not here. One-time setup:

1. Create the repo `maxmoneycash/homebrew-tap` on GitHub.
2. Copy `packaging/turbotokens.rb` to `Formula/turbotokens.rb` there.
3. On each release: update `version` + the three `sha256` values
   (`shasum -a 256` on each release asset) and push.

Users then: `brew install maxmoneycash/tap/turbotokens`.

Getting into `homebrew-core` later (no tap needed): open a PR to
Homebrew/homebrew-core with the same formula once the project has
some traction (they want a notable repo, stable versioning, and a
`test do` block — already included).

## Windows

`turbotokens-windows-x64.zip` is on the Releases page. A Scoop manifest
(`packaging/scoop-turbotokens.json` when we add it) goes in a
`maxmoneycash/scoop-bucket` repo, same pattern as the tap.
