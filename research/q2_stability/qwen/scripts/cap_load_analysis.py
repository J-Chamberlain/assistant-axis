import pandas as pd
import json
import numpy as np
from pathlib import Path

DYAD_CSV = Path("research/q2_stability/qwen/outputs/dyad_v1/all_dyads_summary.csv")
CALIB_JSON = Path("research/q2_stability/qwen/outputs/calibration/all_personas_calibration_summary.json")
OUTPUT_DIR = Path("research/q2_stability/qwen/outputs/dyad_v1")

# Load data
df = pd.read_csv(DYAD_CSV)
with open(CALIB_JSON) as f:
    calib = json.load(f)

# Build per-persona threshold lookup
# calib is a dict keyed by persona name with axis_p25 field
calib_personas = calib.get("personas", calib)
thresholds = {}
for persona, data in calib_personas.items():
    if isinstance(data, dict) and "axis_p25" in data:
        thresholds[persona] = data["axis_p25"]

print("Calibrated thresholds:")
for p, t in thresholds.items():
    print(f"  {p}: {t:.6f}")

# Cap-load inference:
# A turn is considered cap-active if the interviewer axis projection
# is within 10% of the threshold's absolute value above the threshold.
# i.e. cap_active = interviewer_axis <= threshold + 0.1 * abs(threshold)

results = []
for persona in df["persona"].unique():
    threshold = thresholds.get(persona)
    if threshold is None:
        print(f"WARNING: no threshold for {persona}")
        continue
    margin = 0.1 * abs(threshold) if threshold != 0 else 0.01
    cap_zone = threshold + margin

    persona_df = df[df["persona"] == persona]

    for condition in persona_df["condition"].unique():
        cond_df = persona_df[persona_df["condition"] == condition]
        n_turns = len(cond_df)

        interviewer_axis = cond_df["interviewer_axis"]
        interviewer_cosine = cond_df["interviewer_cosine_to_role"]

        cap_active_turns = (interviewer_axis <= cap_zone).sum()
        cap_load_pct = 100 * cap_active_turns / n_turns

        axis_mean = interviewer_axis.mean()
        axis_std = interviewer_axis.std()
        cosine_mean = interviewer_cosine.mean()
        cosine_std = interviewer_cosine.std()

        # Standard model drift
        std_axis = cond_df["standard_axis"]
        std_drift = std_axis.iloc[-1] - std_axis.iloc[0]
        std_axis_mean = std_axis.mean()

        results.append({
            "persona": persona,
            "condition": condition,
            "threshold": threshold,
            "cap_zone_ceiling": cap_zone,
            "n_turns": n_turns,
            "cap_active_turns": int(cap_active_turns),
            "cap_load_pct": round(cap_load_pct, 1),
            "interviewer_axis_mean": round(axis_mean, 4),
            "interviewer_axis_std": round(axis_std, 4),
            "interviewer_cosine_mean": round(cosine_mean, 4),
            "interviewer_cosine_std": round(cosine_std, 4),
            "std_axis_mean": round(std_axis_mean, 4),
            "std_axis_drift": round(std_drift, 4),
        })

results_df = pd.DataFrame(results)

# Print summary table
print("\n=== CAP LOAD AND PERSONA FIDELITY SUMMARY ===")
print(f"{'Persona':<14} {'Condition':<12} {'Cap Load%':>9} {'I-Cosine':>9} {'I-Axis':>8} {'S-Drift':>8}")
print("-" * 65)
for _, row in results_df.sort_values(["persona","condition"]).iterrows():
    print(f"{row['persona']:<14} {row['condition']:<12} "
          f"{row['cap_load_pct']:>8.1f}% "
          f"{row['interviewer_cosine_mean']:>9.4f} "
          f"{row['interviewer_axis_mean']:>8.4f} "
          f"{row['std_axis_drift']:>8.4f}")

# Per-persona summary (averaged across conditions)
print("\n=== PER-PERSONA SUMMARY (mean across conditions) ===")
persona_summary = results_df.groupby("persona").agg(
    cap_load_pct=("cap_load_pct", "mean"),
    interviewer_cosine_mean=("interviewer_cosine_mean", "mean"),
    interviewer_axis_mean=("interviewer_axis_mean", "mean"),
    std_axis_drift=("std_axis_drift", "mean")
).round(3)
print(persona_summary.to_string())

# Flag high cap-load personas (above 60%)
high_load = results_df[results_df["cap_load_pct"] > 60]
if len(high_load) > 0:
    print("\n=== HIGH CAP LOAD CONDITIONS (>60%) ===")
    print(high_load[["persona","condition","cap_load_pct","interviewer_cosine_mean"]].to_string(index=False))

# Flag low persona fidelity (cosine below 0)
low_fidelity = results_df[results_df["interviewer_cosine_mean"] < 0]
if len(low_fidelity) > 0:
    print("\n=== LOW PERSONA FIDELITY (negative cosine) ===")
    print(low_fidelity[["persona","condition","interviewer_cosine_mean","cap_load_pct"]].to_string(index=False))

# Save results
out_path = OUTPUT_DIR / "cap_load_analysis.csv"
results_df.to_csv(out_path, index=False)
print(f"\nSaved to {out_path}")
print("Done.")
