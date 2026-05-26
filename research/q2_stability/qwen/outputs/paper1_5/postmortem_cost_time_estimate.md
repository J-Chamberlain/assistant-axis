# Postmortem Cost and Time Estimate

Audit date: 2026-05-26

## Valid rollout count

- Local snapshot valid Phase 1 records: 1126
- Remaining to reach 1200 from local snapshot: 74
- Live pod had already advanced to at least 1127 records during audit, so actual remaining count may be slightly lower.

## Observed rate

- Latest observed pod checkpoint rate: 27.5 seconds per rollout.
- Latest observed checkpoint: total=1125/1200, think_discards=0, truncated=669, GPU=65.5GB, ETA=0.6hr.

## Remaining time and cost from local snapshot

- Estimated remaining GPU time: 0.57 hours.
- Estimated remaining cost at $1.49/hr: $0.84.
- Estimated remaining cost at $1.51/hr: $0.85.

## Truncation

- Local snapshot truncation count: 670/1126 (59.5%).
- The truncation rate is high enough to flag for Phase 2 interpretation and possible future `max_new_tokens` or prompt changes, but it does not invalidate Phase 1 hidden-state extraction by itself.

## Unattended completion

At the observed rate, the remaining run from the local snapshot is compatible with completing unattended in under 1 hour. The full 1200-run pass at this rate is about 9.2 hours, so a clean rerun would not fit a 1-2 hour window.
