#!/usr/bin/env python3
from liss_common import *
import subprocess

require_files(*EXPECTED_FILES, BIG_FIVE_KEY)
steps = ["verify_liss_2020_sources.py", "validate_liss_2020_schema.py", "score_liss_bigfive.py",
         "score_liss_hifwb.py", "fit_liss_hifwb_measurement_models.py", "fit_liss_personality_wellbeing_models.py"]
records = []
for step in steps:
    completed = subprocess.run([sys.executable, str(ROOT / "scripts" / step)], text=True, capture_output=True)
    records.append({"step": step, "returncode": completed.returncode,
                    "stdout_tail": completed.stdout[-1000:], "stderr_tail": completed.stderr[-1000:]})
    if completed.returncode:
        payload = {"status": "failed", "failed_step": step, "steps": records, "environment": environment_record()}
        write_local_json("pipeline_run.json", payload)
        print(json.dumps(payload, indent=2)); raise SystemExit(completed.returncode)
payload = {"status": "complete", "steps": records, "seed": SEED, "no_external_ai_or_model_inference": True,
           "respondent_rows_written": False, "environment": environment_record()}
write_local_json("pipeline_run.json", payload)
print(json.dumps(payload, indent=2))
