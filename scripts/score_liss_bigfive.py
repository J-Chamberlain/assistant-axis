#!/usr/bin/env python3
from liss_common import *

require_files(CP, CP_CODEBOOK, BIG_FIVE_KEY)
scores = score_big_five(read_stata(CP))
payload = {"status": "scored", "domains": list(scores), "n_nonmissing": scores.notna().sum().astype(int).to_dict(),
           "means": scores.mean().to_dict(), "sds": scores.std().to_dict(), "respondent_rows_written": False}
write_local_json("big_five_score_summary.json", payload)
print(json.dumps(payload, indent=2))
