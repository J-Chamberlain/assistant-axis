# Pod Monitoring Checklist

- Read `heartbeat.json`, not chat memory.
- Check process is alive by PID or command name.
- Count JSONL records and activation shards.
- Inspect latest log lines for rollout count, discard count, truncation count, rate, ETA, and errors.
- Check GPU memory and disk free space.
- Copy a partial snapshot only if useful for recovery.
- Label partial snapshots as partial.
- Update run registry or `RESEARCH_STATE.md` with the observed state.
- Do not terminate while the run is healthy and outputs are not final-preserved.
