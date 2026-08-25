//! Argument parsing and `--help` rendering for the turbotokens CLI.
//!
//! Split from `turbotokens-cli`, which holds the plain argument types the runtime
//! crates need: the parser embeds the generated help tables through a build
//! script, so keeping it here means editing help text does not invalidate
//! turbotokens-core or any adapter.
use turbotokens_cli::{Command, SharedArgs};

mod arg_parser;
mod help;
mod parser;

pub struct Cli {
    pub command: Option<Command>,
    pub shared: SharedArgs,
}

#[cfg(test)]
mod help_codegen;

#[cfg(test)]
mod tests;
