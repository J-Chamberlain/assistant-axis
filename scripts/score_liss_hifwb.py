#!/usr/bin/env python3
from liss_common import *

require_files(SS, SS_CODEBOOK)
scores = score_hifwb(read_stata(SS))
if scores.empty:
    raise SystemExit("no crosswalk variables found in SS source")
content_columns = [c for c in scores if not c.endswith("__valid_items") and c not in {"questionnaire_version", "timeframe"}]
summary = scores.groupby(["questionnaire_version", "timeframe"])[content_columns].agg(["count", "mean", "std"])
payload = {"status": "scored_by_randomized_form", "summary": json.loads(summary.to_json(orient="table")), "respondent_rows_written": False}
write_local_json("hifwb_score_summary.json", payload)
print(json.dumps(payload, indent=2))
