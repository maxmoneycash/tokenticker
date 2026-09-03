use std::time::Duration;

const PRICING_FETCH_TIMEOUT_SECONDS: u64 = 10;
const PRICING_FETCH_MAX_BYTES: u64 = 64 * 1024 * 1024;

/// Fetches a JSON document for the pricing refresh.
///
/// This lives in the binary so that `ureq` and its TLS stack are not dependencies
/// of `turbotokens-core`, which every adapter builds against; `main` installs it
/// through `turbotokens_core::pricing::set_json_fetcher`.
pub(crate) fn fetch_json(url: &str) -> std::io::Result<String> {
    let agent = ureq::Agent::config_builder()
        .timeout_global(Some(Duration::from_secs(PRICING_FETCH_TIMEOUT_SECONDS)))
        .build()
        .new_agent();
    let mut response = agent
        .get(url)
        .call()
        .map_err(|error| std::io::Error::other(error.to_string()))?;
    if response.status().as_u16() != 200 {
        return Err(std::io::Error::other(format!(
            "HTTP {}",
            response.status().as_u16()
        )));
    }
    response
        .body_mut()
        .with_config()
        .limit(PRICING_FETCH_MAX_BYTES)
        .read_to_string()
        .map_err(|error| std::io::Error::new(std::io::ErrorKind::InvalidData, error.to_string()))
}

const LIMITS_FETCH_MAX_BYTES: u64 = 1024 * 1024;

/// Fetches a JSON document with caller-supplied request headers, for the
/// authenticated plan-limit endpoints (`turbotokens limits`).
///
/// Callers own the headers — this never logs them, and error messages carry
/// only the HTTP status, never the response body.
pub(crate) fn fetch_json_with_headers(
    url: &str,
    headers: &[(&str, &str)],
) -> std::io::Result<String> {
    let agent = ureq::Agent::config_builder()
        .timeout_global(Some(Duration::from_secs(PRICING_FETCH_TIMEOUT_SECONDS)))
        .http_status_as_error(false)
        .build()
        .new_agent();
    let mut request = agent.get(url);
    for &(name, value) in headers {
        request = request.header(name, value);
    }
    let mut response = request
        .call()
        .map_err(|error| std::io::Error::other(error.to_string()))?;
    let status = response.status().as_u16();
    if status != 200 {
        return Err(std::io::Error::other(format!("HTTP {status}")));
    }
    response
        .body_mut()
        .with_config()
        .limit(LIMITS_FETCH_MAX_BYTES)
        .read_to_string()
        .map_err(|error| std::io::Error::new(std::io::ErrorKind::InvalidData, error.to_string()))
}
