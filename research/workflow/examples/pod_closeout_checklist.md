# Pod Closeout Checklist

- Confirm the run reached its planned completion condition or user-approved stop condition.
- Preserve JSONL, activation shards, logs, manifest, heartbeat, and executed script locally.
- Run local integrity validation.
- Save `integrity.json` and any Markdown decision report.
- Confirm activation shards are ignored by Git unless explicitly intended.
- Run scoring only after integrity passes.
- Run vector or metric validation only after scoring produces the required subset.
- Terminate the pod through RunPod API or CLI when possible.
- Save `termination.json` with confirmation evidence.
- Update run registry to `terminated`.
- Commit and push safe artifacts.
