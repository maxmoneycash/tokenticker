use std::{env, fs};

const WORKSPACE_TOML: &str = "../../Cargo.toml";
const VERSION_ENV: &str = "TURBOTOKENS_VERSION";

fn main() {
    println!("cargo:rerun-if-env-changed={VERSION_ENV}");
    println!("cargo:rerun-if-changed={WORKSPACE_TOML}");
    let version = env::var(VERSION_ENV).unwrap_or_else(|_| workspace_version());
    println!("cargo:rustc-env={VERSION_ENV}={version}");
}

/// Reads `[workspace.package].version` from the workspace manifest so the
/// binary version is bumped in exactly one place.
fn workspace_version() -> String {
    let toml = fs::read_to_string(WORKSPACE_TOML).expect("read workspace Cargo.toml");
    let mut in_package = false;
    for line in toml.lines() {
        let line = line.trim();
        if line.starts_with('[') {
            in_package = line == "[workspace.package]";
            continue;
        }
        if in_package && let Some(value) = line.strip_prefix("version") {
            return value
                .trim_start_matches(['=', ' ', '\t', '"'])
                .trim_end_matches('"')
                .to_owned();
        }
    }
    panic!("read version from workspace Cargo.toml");
}
