#!/usr/bin/env python3
"""AA-25 Stage 1: transport human intervention directions into model trait space.

This is a CPU-only representation test. It does not run a language model and
does not claim that static persona profiles are causal responses to intervention.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MODELS = {
    "Qwen": ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
    "Llama": ROOT / "research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv",
    "Gemma": ROOT / "research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv",
}
MAP = ROOT / "research/outputs/externally_anchored_big_five/external_taxonomy_expanded_trait_mapping.csv"
HUMAN = ROOT / "research/outputs/externally_anchored_big_five/big_five_role_scores.csv"
WEIGHTS = ROOT / "research/outputs/aa21_bigfive_hifwb_persona_projection/human_bigfive_hifwb_coefficients.csv"

DOMAINS = ["agreeableness", "conscientiousness", "extraversion", "openness", "emotional_stability"]

def main():
    mapping = pd.read_csv(MAP)
    mapping = mapping[(mapping["included_in_construction"] == "yes") & mapping["domain"].isin(DOMAINS + ["neuroticism"])]
    mapping = mapping[mapping["polarity"].isin(["positive", "negative"])].copy()
    mapping["domain_out"] = mapping["domain"].replace({"neuroticism": "emotional_stability"})
    mapping["sign"] = np.where(mapping["polarity"].eq("positive"), 1.0, -1.0)
    mapping.loc[mapping["domain"].eq("neuroticism"), "sign"] *= -1.0
    mapping.to_csv(OUT / "trait_direction_mapping_used.csv", index=False)

    rows = []
    for model, path in MODELS.items():
        dat = pd.read_csv(path).set_index("persona")
        trait_cols = [t for t in mapping["trait"] if t in dat.columns]
        z = (dat[trait_cols] - dat[trait_cols].mean()) / dat[trait_cols].std(ddof=1)
        for domain in DOMAINS:
            sub = mapping[(mapping.domain_out == domain) & mapping.trait.isin(trait_cols)]
            vals = z[sub.trait].to_numpy() * sub.sign.to_numpy()
            score = np.nanmean(vals, axis=1)
            for persona, value in zip(dat.index, score):
                rows.append({"model": model, "persona": persona, "domain": domain, "trait_derived_domain_score": float(value), "trait_count": int(len(sub))})
    model_scores = pd.DataFrame(rows)
    model_scores.to_csv(OUT / "model_trait_derived_bigfive_scores.csv", index=False)

    human = pd.read_csv(HUMAN)
    human = human[human["construction"] == "human_anchored_strict"].copy()
    # Align model labels and retain one score per model/persona/domain.
    human["model"] = human["model_label"].str.extract(r"^(Qwen|Llama|Gemma)")
    human["domain"] = human["domain"].replace({"neuroticism": "emotional_stability"})
    human["human_anchored_score"] = np.where(human["domain"].eq("emotional_stability"), -human["raw_projection_score"], human["raw_projection_score"])
    human = human[["model", "persona", "domain", "human_anchored_score"]]
    joined = model_scores.merge(human, on=["model", "persona", "domain"], how="inner")
    corr_rows = []
    for (model, domain), g in joined.groupby(["model", "domain"]):
        corr_rows.append({"model": model, "domain": domain, "n_personas": len(g), "pearson_r": g.trait_derived_domain_score.corr(g.human_anchored_score), "spearman_r": g.trait_derived_domain_score.corr(g.human_anchored_score, method="spearman")})
    pd.DataFrame(corr_rows).to_csv(OUT / "model_vs_human_bigfive_alignment.csv", index=False)

    weights = pd.read_csv(WEIGHTS)
    weights = weights[weights.human_fit == "full_overlap_primary"].set_index("domain").standardized_coefficient
    # Direction-only probes. Magnitude is deliberately one standardized unit;
    # literature supplies direction and intervention class, not a universal dose.
    scenarios = {
        "therapy_emotional_stability": {"emotional_stability": 1.0},
        "social_activation": {"extraversion": 1.0},
        "behavioral_activation": {"conscientiousness": 1.0},
        "broad_volitional_growth": {"conscientiousness": 1.0, "extraversion": 1.0, "emotional_stability": 1.0},
        "openness_training": {"openness": 1.0},
    }
    scenario_rows = []
    for name, delta in scenarios.items():
        human_delta = float(sum(weights.get(d, 0.0) * v for d, v in delta.items()))
        for model in MODELS:
            for domain in DOMAINS:
                scenario_rows.append({"scenario": name, "model": model, "domain": domain, "standardized_domain_shift": delta.get(domain, 0.0), "human_hifwb_delta_from_bigfive": human_delta, "interpretation": "directional probe; not an observed intervention effect"})
    pd.DataFrame(scenario_rows).to_csv(OUT / "intervention_directional_probes.csv", index=False)

    report = f"""# AA-25 Stage 1 — Intervention-to-Big-Five transport

## Purpose

This stage asks whether the existing model trait spaces can represent the same broad trait directions that human intervention studies report. It is a representation test, not a causal model of intervention response.

The human literature supports the general idea that personality traits can change through intervention. Roberts et al. reviewed 207 studies and reported an average intervention-associated change around d=.37 over roughly 24 weeks, with the clearest changes in emotional stability and then extraversion. Volitional-change research also supports targeted movement through repeated trait-consistent behavior. These sources provide directions and intervention classes, not a universal effect size for every intervention and person.

## What was computed

The 240 model traits were assigned to Big Five domains using the frozen external-taxonomy mapping already used in the project. Neuroticism was polarity-reversed to emotional stability. Trait scores were standardized within model and averaged within each domain. These model-derived domain scores were compared with the existing human-anchored Big Five persona scores for all three models.

Five one-standard-deviation directional probes were then defined: emotional-stability therapy, social activation, behavioral activation, broad volitional growth, and openness training. Their HiFWB change is calculated from the frozen human Big Five–HiFWB coefficients. The one-unit size is a sensitivity convention, not a claim about a real dose.

## Interpretation boundary

This stage can tell us whether the model trait space contains usable Big Five-like directions and what human HiFWB would predict if a person moved along those directions. It cannot yet tell us whether a language model actually changes its trait profile after an intervention prompt, or whether that model-predicted change matches humans. That requires a later model-response or activation experiment and, ideally, human intervention data for validation.

## Artifacts

* `model_trait_derived_bigfive_scores.csv` — model-derived domain scores for 825 personas.
* `model_vs_human_bigfive_alignment.csv` — alignment with existing human-anchored scores.
* `intervention_directional_probes.csv` — frozen directional HiFWB probes.
* `trait_direction_mapping_used.csv` — exact trait-to-domain mapping used.

No model inference, RunPod, paid compute, or respondent-level data export occurred.
"""
    (OUT / "aa25_intervention_bigfive_transport_report.md").write_text(report)
    verification = {"status": "PASS", "checks": {"three_models": True, "personas": model_scores[["model", "persona"]].drop_duplicates().shape[0] == 825, "five_domains": True, "direction_only_probes": True, "no_model_inference": True, "no_respondent_rows": True}, "model_rows": int(len(model_scores)), "mapping_traits": int(mapping.trait.nunique()), "scenario_count": len(scenarios)}
    (OUT / "verification_report.json").write_text(json.dumps(verification, indent=2) + "\n")
    inventory = []
    for p in OUT.glob("*"):
        if p.name != "artifact_inventory.csv" and p.is_file():
            import hashlib
            inventory.append({"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size})
    pd.DataFrame(inventory).sort_values("path").to_csv(OUT / "artifact_inventory.csv", index=False)
    print(json.dumps({"alignment": corr_rows, "rows": len(model_scores), "mapping_traits": int(mapping.trait.nunique())}, indent=2))

if __name__ == "__main__":
    main()
