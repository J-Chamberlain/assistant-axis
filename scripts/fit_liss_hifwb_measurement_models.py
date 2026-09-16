#!/usr/bin/env python3
from liss_common import *

require_files(SS, SS_CODEBOOK)
try:
    import pandas as pd
    from semopy import Model, calc_stats
except ImportError as exc:
    raise SystemExit(f"semopy is required after data arrival for the frozen measurement program: {exc}")

frame, mapping = read_stata(SS), hifwb_item_map()
mapping = mapping[mapping["mapping_status"].isin(["DIRECT", "CLOSE"])]
results = []
for version, rows in mapping.groupby("questionnaire_version"):
    routed = frame.loc[pd.to_numeric(frame["ss20a001"], errors="coerce") == int(version)]
    groups = {content: [v for v in block["variable"] if v in routed] for content, block in rows.groupby("hifwb_content")}
    groups = {k: v for k, v in groups.items() if len(v) >= 2}
    all_items = sum(groups.values(), [])
    safe = {k.replace(" ", "_").replace("-", "_"): v for k, v in groups.items()}
    measurement = [f"{name} =~ {' + '.join(items)}" for name, items in safe.items()]
    models = {
        "general": [f"h =~ {' + '.join(all_items)}"],
        "correlated_contents": measurement,
        "hifwb_higher_order": measurement + ["Subjective =~ Affect + Appraisal", "Psychological =~ Meaning_making + Self_concept",
                                                "Social =~ Community + Interpersonal_relationships", "h =~ Subjective + Psychological + Social"],
        "bifactor": [f"h =~ {' + '.join(all_items)}"] + measurement + [f"h ~~ 0*{name}" for name in safe],
    }
    for name, syntax in models.items():
        record = {"version": int(version), "timeframe": rows["timeframe"].iloc[0], "model": name, "n": len(routed)}
        try:
            model = Model("\n".join(syntax))
            model.fit(routed[all_items], obj="FIML")
            stats = calc_stats(model).iloc[0]
            record.update(status="fit", CFI=float(stats.get("CFI")), TLI=float(stats.get("TLI")), RMSEA=float(stats.get("RMSEA")),
                          AIC=float(stats.get("AIC")), BIC=float(stats.get("BIC")))
        except Exception as exc:
            record.update(status="failed_or_unidentified", diagnostic=type(exc).__name__ + ": " + str(exc)[:240])
        results.append(record)
payload = {"status": "complete_with_model_specific_diagnostics", "models": results,
           "esem_status": "requires a supported ESEM implementation; not silently approximated", "respondent_rows_written": False,
           "environment": environment_record()}
write_local_json("measurement_model_summary.json", payload)
print(json.dumps(payload, indent=2))
