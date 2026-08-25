use std::collections::{HashMap, HashSet};

use crate::{
    LoadedEntry, PricingMap, Result, cli::SharedArgs, debug_log, parse_tz, read_files_parallel,
};

use super::{
    parser::{
        ModelTimelines, grok_entry_key, grok_entry_to_loaded, read_model_events, read_usage_log,
    },
    paths::{discover_event_files, discover_usage_logs},
};

pub fn load_entries(shared: &SharedArgs, pricing: &PricingMap) -> Result<Vec<LoadedEntry>> {
    crate::progress::track_usage_load(
        crate::progress::UsageLoadAgent("Grok Build"),
        shared.json,
        || load_entries_inner(shared, pricing),
    )
}

fn load_entries_inner(shared: &SharedArgs, pricing: &PricingMap) -> Result<Vec<LoadedEntry>> {
    let event_files = discover_event_files()?;
    let loaded_events = read_files_parallel(&event_files, shared.single_thread, |file| {
        read_model_events(file).unwrap_or_else(|error| {
            debug_log(
                shared,
                format!(
                    "Failed to read Grok Build turn events {}: {error}",
                    file.display()
                ),
            );
            Vec::new()
        })
    });
    let mut timelines = HashMap::new();
    for file_events in loaded_events {
        for (session_id, event) in file_events {
            timelines
                .entry(session_id)
                .or_insert_with(Vec::new)
                .push(event);
        }
    }
    sort_timelines(&mut timelines);

    let tz = parse_tz(shared.timezone.as_deref());
    let usage_logs = discover_usage_logs();
    let loaded = read_files_parallel(&usage_logs, shared.single_thread, |file| {
        read_usage_log(file, &timelines).unwrap_or_else(|error| {
            debug_log(
                shared,
                format!(
                    "Failed to read Grok Build usage log {}: {error}",
                    file.display()
                ),
            );
            Vec::new()
        })
    });
    let mut entries = Vec::new();
    let mut seen = HashSet::new();
    for file_entries in loaded {
        for entry in file_entries {
            if seen.insert(grok_entry_key(&entry)) {
                entries.push(grok_entry_to_loaded(
                    entry,
                    tz.as_ref(),
                    shared.mode,
                    pricing,
                ));
            }
        }
    }
    entries.sort_by_key(|entry| entry.timestamp);
    Ok(entries)
}

fn sort_timelines(timelines: &mut ModelTimelines) {
    for events in timelines.values_mut() {
        events.sort_by_key(|event| event.timestamp);
        events
            .dedup_by(|left, right| left.timestamp == right.timestamp && left.model == right.model);
    }
}

#[cfg(test)]
mod tests {
    use super::super::paths::{GROK_HOME_ENV, GROK_HOME_LOCK};
    use super::*;
    use turbotokens_test_support::{EnvVarGuard, fs_fixture};

    #[test]
    fn loads_grok_inference_usage_with_the_active_turn_model() {
        let _guard = GROK_HOME_LOCK.lock().unwrap();
        let fixture = fs_fixture!({
            "logs/unified.jsonl": [
                r#"{"ts":"2026-07-08T07:10:13.766Z","src":"shell","sid":"session-a","msg":"shell.turn.inference_done","ctx":{"loop_index":1,"prompt_tokens":36458,"cached_prompt_tokens":32876,"completion_tokens":251,"reasoning_tokens":99}}"#,
                "not json",
            ].join("\n"),
            "sessions/workspace/session-a/events.jsonl": r#"{"type":"turn_started","ts":"2026-07-08T07:00:00.000Z","session_id":"session-a","model_id":"grok-4.5","turn_number":0}"#,
        });
        let _env = EnvVarGuard::set(GROK_HOME_ENV, fixture.root());
        let shared = SharedArgs {
            timezone: Some("UTC".to_string()),
            offline: true,
            single_thread: true,
            ..SharedArgs::default()
        };

        let entries = load_entries(&shared, &PricingMap::load_embedded()).unwrap();

        assert_eq!(entries.len(), 1);
        assert_eq!(entries[0].date, "2026-07-08");
        assert_eq!(entries[0].session_id.as_ref(), "session-a");
        assert_eq!(entries[0].model.as_deref(), Some("grok-4.5"));
        assert_eq!(entries[0].data.message.usage.input_tokens, 3_582);
        assert_eq!(
            entries[0].data.message.usage.cache_read_input_tokens,
            32_876
        );
        assert_eq!(entries[0].data.message.usage.output_tokens, 251);
        assert_eq!(entries[0].extra_total_tokens, 99);
        assert!((entries[0].cost - 0.019_126_8).abs() < f64::EPSILON);

        let rows = crate::summarize_entries(&entries, crate::cli::AgentReportKind::Daily).unwrap();
        let report = crate::report_from_rows(&rows, crate::cli::AgentReportKind::Daily);
        assert_eq!(report["daily"][0]["totalTokens"], 36_808);
        assert_eq!(report["totals"]["totalTokens"], 36_808);
    }

    #[test]
    #[ignore = "requires local Grok Build logs under ~/.grok"]
    fn local_grok_build_data_smoke_test() {
        let _guard = GROK_HOME_LOCK.lock().unwrap();
        let shared = SharedArgs {
            timezone: Some("UTC".to_string()),
            offline: true,
            single_thread: false,
            ..SharedArgs::default()
        };

        let entries = load_entries(&shared, &PricingMap::load_embedded()).unwrap();

        assert!(!entries.is_empty());
        assert!(entries.iter().all(|entry| entry.project.as_ref() == "grok"));
        assert!(entries.iter().all(|entry| entry.timestamp.as_millis() > 0));
    }
}
