#!/usr/bin/env python3
"""Build a dependency-light Paper 1.5 core walkthrough notebook.

The local Mac Mini Python used by Codex does not necessarily include Jupyter,
pandas, or matplotlib. This script writes valid notebook JSON directly and then
performs a clean plain-Python execution pass over the code cells.
"""

from __future__ import annotations

import ast
import csv
import datetime as dt
import json
import traceback
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK_PATH = REPO_ROOT / "research/notebooks/paper15_core_analysis_walkthrough.ipynb"
OUT_DIR = REPO_ROOT / "research/outputs/paper15_notebook_core"
FIG_DIR = OUT_DIR / "figures"


DEPENDENCIES = [
    ("N00", "research/outputs/paper15_clean_repo_copy_plan/clean_repo_copy_plan.csv", "Copy-plan artifact inventory and canonical status counts.", "paper15_clean_repo_copy_plan", "Required; loaded with stdlib CSV."),
    ("N00", "research/outputs/paper15_clean_repo_copy_plan/canonical_claims_traceability_table.csv", "Traceability table for report-spine claims.", "paper15_clean_repo_copy_plan", "Required; unverified rows remain visible."),
    ("N01", "research/visualizations/geometry_viz_data.json", "Public persona/trait geometry, Qwen role coordinates, clusters, and available model geometry.", "visualizations", "Primary geometry source."),
    ("N01", "research/outputs/prompt_artifact_inventory/role_prompt_artifact_index.csv", "Role prompt artifact inventory.", "prompt_artifact_inventory", "Used for count and instruction structure summary."),
    ("N01", "research/outputs/prompt_artifact_inventory/trait_prompt_artifact_index.csv", "Trait prompt artifact inventory.", "prompt_artifact_inventory", "Used for count and instruction structure summary."),
    ("N01", "research/outputs/role_rollout_artifact_audit/role_prompt_reconstruction_inventory.csv", "Role 5x240 input reconstruction inventory.", "role_rollout_artifact_audit", "Confirms theoretical 1,200 inputs per role and public-response limitations."),
    ("N02", "research/outputs/cross_model_pc2_pc3_diagnostic/cross_model_pc_correlation_matrix.csv", "Cross-model PC correlation matrix.", "cross_model_pc2_pc3_diagnostic", "Pre-H100 cross-model caveat source."),
    ("N02", "research/outputs/cross_model_pc2_pc3_diagnostic/cross_model_pc_best_matches.csv", "Best matching PCs across models.", "cross_model_pc2_pc3_diagnostic", "Used for Qwen/Llama PC2-PC3 caveats."),
    ("N02", "research/outputs/cross_model_cluster_topology/cross_model_cluster_similarity_metrics.json", "Cross-model cluster topology metrics.", "cross_model_cluster_topology", "Used for bounded cluster-transfer summary."),
    ("N04", "research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_top_bottom.csv", "Muted-PC1 PC2 extreme roles.", "pc2_muted_pc1_extremes", "Supports PC2 provisional interpretation."),
    ("N04", "research/outputs/pc2_cluster_conditioned_extremes/pc2_diagnostic_roles_table.csv", "PC2 diagnostic role table.", "pc2_cluster_conditioned_extremes", "Supports PC2 counterexample inspection."),
    ("N04", "research/outputs/pc2_cluster_conditioned_extremes/pc2_expected_direction_checks.csv", "PC2 expected-direction checks.", "pc2_cluster_conditioned_extremes", "Supports global/cluster pass-rate summary."),
    ("N05", "research/outputs/pc3_validation/pc3_validation_stats.json", "PC3 perturbation/stabilization validation stats.", "pc3_validation", "Supports PC3 metrics table."),
    ("N06", "research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json", "Trait-profile prediction of persona PCs.", "trait_persona_prediction", "Supports same-space trait/persona result."),
    ("N06", "research/outputs/trait_space_interpretation/trait_space_validation_stats.json", "Trait-only PCA and trait/persona PC comparison.", "trait_space_interpretation", "Supports layered-geometry caveat."),
    ("N08", "research/outputs/prompt_to_geometry_forecasting/forecasting_results.json", "Prompt-to-geometry forecasting result summary.", "prompt_to_geometry_forecasting", "Pre-H100 intended-address forecasting baseline."),
    ("N08", "research/outputs/prompt_to_geometry_forecasting/forecasting_model_comparison.csv", "Prompt-to-geometry model comparison.", "prompt_to_geometry_forecasting", "Used for held-out role/trait metric table."),
    ("N09", "research/visualizations/persona_geometry_explorer.html", "Main Persona Geometry Explorer.", "visualizations", "Linked only; visualization files are not modified."),
]


CLAIMS = [
    ("Public role geometry contains 275 non-default roles and 240 traits.", "N01", "research/visualizations/geometry_viz_data.json; prompt artifact inventories", "role/trait counts", "canonical", "Counts are public-artifact-level, not regenerated activations."),
    ("Role-vector input prompts are reconstructable as 5 positive instructions x 240 shared questions per role.", "N01", "research/outputs/role_rollout_artifact_audit/role_prompt_reconstruction_inventory.csv", "theoretical_input_combinations", "canonical", "Generated responses and judge filters are not public."),
    ("PC1 is the strongest axis and is interpreted as convergence pressure versus degrees of freedom.", "N03", "research/visualizations/geometry_viz_data.json; axis forcing-function notes", "top/bottom PC1 roles", "interpretive", "Endpoint roles are evidence, not the causal interpretation."),
    ("PC2 is provisionally interpreted as situated-immediacy/formative-state versus integrated-stability.", "N04", "research/outputs/pc2_cluster_conditioned_extremes/", "expected-direction checks and diagnostic roles", "provisional", "Shapeshifter, chameleon, and elder complicate a simple reading."),
    ("PC3 supports perturbation/intervention versus stabilization/repair better than moral valence alone.", "N05", "research/outputs/pc3_validation/pc3_validation_stats.json", "Pearson/Spearman/pairwise ordering", "supported", "Rubric scores are deterministic, not independent human ratings."),
    ("Trait profiles predict persona PC coordinates strongly, but trait-only PCA does not simply replace persona PCA.", "N06", "research/outputs/trait_persona_prediction/; research/outputs/trait_space_interpretation/", "R2 and PC alignment metrics", "supported", "Same-space reconstruction is not a claim of psychological ontology."),
    ("Prediction-improvement numbers should only be used when traceable to canonical files.", "N07", "research/outputs/paper15_clean_repo_copy_plan/canonical_claims_traceability_table.csv", "verified/unverified claim rows", "workflow", "Unverified remembered numbers are excluded from canonical claims."),
    ("Prompt-to-geometry forecasting is an intended-address predictor, not yet H100 response-state validation.", "N08", "research/outputs/prompt_to_geometry_forecasting/", "held-out forecasting metrics", "supported_pre_h100", "Execution-time activation validation is deferred."),
    ("Cross-model topology is partially conserved, but PC2/PC3 require caveats.", "N02", "research/outputs/cross_model_pc2_pc3_diagnostic/; research/outputs/cross_model_cluster_topology/", "PC correlations and ARI/NMI", "provisional", "Hard clusters are not universal; PC3 is weaker across models."),
]


CELL_COUNTER = 0


def next_cell_id() -> str:
    global CELL_COUNTER
    CELL_COUNTER += 1
    return f"paper15-{CELL_COUNTER:03d}"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "id": next_cell_id(), "metadata": {}, "source": source.strip() + "\n"}


def code(source: str) -> dict:
    return {"cell_type": "code", "id": next_cell_id(), "execution_count": None, "metadata": {}, "outputs": [], "source": source.strip() + "\n"}


SETUP_CODE = r'''
from pathlib import Path
import csv, json, math, statistics, textwrap

def find_repo_root():
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "research" / "RESEARCH_STATE.md").exists():
            return p
    raise RuntimeError("Could not find repo root from current working directory.")

REPO_ROOT = find_repo_root()
OUT_DIR = REPO_ROOT / "research" / "outputs" / "paper15_notebook_core"
FIG_DIR = OUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
print("Repo root:", REPO_ROOT)

def rel(path):
    return Path(path)

def exists(path):
    return (REPO_ROOT / path).exists()

def load_csv(path):
    p = REPO_ROOT / path
    if not p.exists():
        print("MISSING:", path)
        return []
    with p.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def load_json(path):
    p = REPO_ROOT / path
    if not p.exists():
        print("MISSING:", path)
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def fnum(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def table(rows, columns=None, limit=12):
    rows = list(rows or [])
    if not rows:
        print("(no rows)")
        return
    if columns is None:
        columns = list(rows[0].keys())
    clipped = rows[:limit]
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in clipped)) for c in columns}
    print(" | ".join(str(c).ljust(widths[c]) for c in columns))
    print("-+-".join("-" * widths[c] for c in columns))
    for r in clipped:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))
    if len(rows) > limit:
        print(f"... {len(rows) - limit} more rows")

def rows_by_count(rows, key):
    counts = {}
    for r in rows:
        counts[r.get(key, "")] = counts.get(r.get(key, ""), 0) + 1
    return [{key: k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]

def role_dataframe_from_geometry(geometry):
    roles = geometry["roles"]
    records = []
    for name, coords, cluster in zip(roles["names"], roles["pca3d"], roles.get("clusters", [""] * len(roles["names"]))):
        records.append({"role": name, "pc1": coords[0], "pc2": coords[1], "pc3": coords[2], "cluster": cluster})
    for axis in ["pc1", "pc2", "pc3"]:
        vals = sorted(r[axis] for r in records)
        n = len(vals)
        for r in records:
            rank = sum(v <= r[axis] for v in vals)
            r[axis + "_percentile"] = 100 * (rank - 1) / max(n - 1, 1)
    return records

def top_bottom(rows, axis, n=15):
    top = sorted(rows, key=lambda r: r[axis], reverse=True)[:n]
    bottom = sorted(rows, key=lambda r: r[axis])[:n]
    return top, bottom

def safe_plot_pc_scatter(rows, x="pc1", y="pc2", labels=None, out_name="scatter.png"):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print("matplotlib unavailable; skipping plot:", exc)
        return None
    labels = set(labels or [])
    xs = [r[x] for r in rows]
    ys = [r[y] for r in rows]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(xs, ys, s=14, alpha=0.5)
    for r in rows:
        if r["role"] in labels:
            ax.annotate(r["role"], (r[x], r[y]), fontsize=8)
    ax.axhline(0, color="0.85", linewidth=1)
    ax.axvline(0, color="0.85", linewidth=1)
    ax.set_xlabel(x.upper())
    ax.set_ylabel(y.upper())
    ax.set_title(f"Qwen role geometry: {x.upper()} vs {y.upper()}")
    out = FIG_DIR / out_name
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print("Saved", out.relative_to(REPO_ROOT))
    return out
'''


NOTEBOOK_CELLS = [
    md("# Assistant Axis Reanalysis: Public Geometry, Axis Interpretation, and Forecasting Baselines\n\nThis notebook is an executable appendix for the Paper 1.5 work-in-progress. It starts from canonical pre-H100 artifacts in the full research repo and stops before execution-time H100 validation, prompt-battery generation, extraction-boundary diagnostics, RunPod logs, and forecast-vs-observed arrow tools."),
    md("## N00. Setup and Provenance\n\nQuestion: which canonical pre-H100 artifacts are available for the walkthrough?\n\nData loaded: the clean-repo copy plan and canonical claim traceability table.\n\nMethod: use standard-library CSV/JSON loaders so the notebook can run in a minimal local Python kernel.\n\nResult shown: artifact counts by type/status and unresolved review rows.\n\nCaveat: this is a notebook skeleton, not a final paper or clean repo copy."),
    code(SETUP_CODE),
    code('''
copy_plan = load_csv("research/outputs/paper15_clean_repo_copy_plan/clean_repo_copy_plan.csv")
claim_trace = load_csv("research/outputs/paper15_clean_repo_copy_plan/canonical_claims_traceability_table.csv")
print("Copy-plan rows:", len(copy_plan))
print("Claim-trace rows:", len(claim_trace))
print("\\nCanonical status counts:")
table(rows_by_count(copy_plan, "canonical_status"), ["canonical_status", "count"], limit=20)
print("\\nArtifact type counts:")
table(rows_by_count(copy_plan, "artifact_type"), ["artifact_type", "count"], limit=20)
print("\\nRows needing user review or unresolved status:")
review = [r for r in copy_plan if "review" in r.get("canonical_status", "") or "unresolved" in r.get("canonical_status", "")]
table(review, ["source_path", "canonical_status", "notes_or_uncertainties"], limit=12)
'''),
    md("## N01. Public Geometry and Artifact Reconstruction\n\nQuestion: what public geometry and prompt artifacts anchor the analysis?\n\nData loaded: `research/visualizations/geometry_viz_data.json`, prompt artifact inventories, and role rollout reconstruction inventory.\n\nMethod: inspect schema, count roles/traits, summarize clusters, and verify public input basis.\n\nResult shown: model/role counts, cluster counts, and prompt artifact component counts.\n\nCaveat: public artifacts allow intended input reconstruction, but generated responses and response-level judge filters are not public."),
    code('''
geometry = load_json("research/visualizations/geometry_viz_data.json")
print("Geometry metadata:", geometry.get("metadata", {}))
roles_df = role_dataframe_from_geometry(geometry)
print("Role count:", len(roles_df))
print("Trait count:", len(geometry.get("traits", {}).get("names", [])))
print("\\nCluster counts:")
table(rows_by_count(roles_df, "cluster"), ["cluster", "count"], limit=20)

role_artifacts = load_csv("research/outputs/prompt_artifact_inventory/role_prompt_artifact_index.csv")
trait_artifacts = load_csv("research/outputs/prompt_artifact_inventory/trait_prompt_artifact_index.csv")
rollout_inventory = load_csv("research/outputs/role_rollout_artifact_audit/role_prompt_reconstruction_inventory.csv")
artifact_summary = [
    {"component": "role prompt artifacts", "rows": len(role_artifacts), "source": "role_prompt_artifact_index.csv"},
    {"component": "trait prompt artifacts", "rows": len(trait_artifacts), "source": "trait_prompt_artifact_index.csv"},
    {"component": "role reconstruction inventory", "rows": len(rollout_inventory), "source": "role_prompt_reconstruction_inventory.csv"},
    {"component": "shared extraction questions", "rows": sum(1 for _ in (REPO_ROOT / "data/extraction_questions.jsonl").open(encoding="utf-8")) if exists("data/extraction_questions.jsonl") else "missing", "source": "data/extraction_questions.jsonl"},
]
table(artifact_summary, ["component", "rows", "source"], limit=10)
non_default = [r for r in rollout_inventory if r.get("is_default") == "False"]
combo_counts = sorted(set(r.get("theoretical_input_combinations") for r in non_default))
print("Non-default roles in rollout inventory:", len(non_default))
print("Theoretical combinations per non-default role:", combo_counts)
print("Example reconstruction row:")
table(non_default[:1], ["role", "positive_instruction_count", "global_extraction_question_count", "theoretical_input_combinations", "first_instruction"], limit=1)
'''),
    md("**Metadata clarification.** In the geometry file, `source_model: Qwen/Qwen3-32B` is the model whose public role/persona vectors are being analyzed in the Qwen sections. The `model_used: GPT-5.5` field is project metadata for the analysis/helper that prepared this visualization data, not the source model for the role-vector geometry."),
    md("## N02. Cross-Model Scope and Caveats\n\nQuestion: how model-general are the relevant axes and broad topology?\n\nData loaded: cross-model PC correlations, best-match PCs, and cluster topology metrics.\n\nMethod: display Qwen-Llama correlations and ARI/NMI cluster alignment summaries.\n\nResult shown: PC2 partly transfers inside a shared PC1/PC2 subspace; PC3 is weaker; clusters are partially conserved.\n\nCaveat: cross-model hard clusters and same-index later PCs should not be treated as universal without alignment caveats."),
    code('''
pc_corr = load_csv("research/outputs/cross_model_pc2_pc3_diagnostic/cross_model_pc_correlation_matrix.csv")
best_matches = load_csv("research/outputs/cross_model_pc2_pc3_diagnostic/cross_model_pc_best_matches.csv")
cluster_metrics = load_json("research/outputs/cross_model_cluster_topology/cross_model_cluster_similarity_metrics.json")
ql_same = [r for r in pc_corr if r["model_a"] == "qwen" and r["model_b"] == "llama" and r["pc_a"] == r["pc_b"]]
print("Qwen-Llama same-index PC correlations:")
table(ql_same, ["pc_a", "matched_role_count", "pearson_r", "spearman_r"], limit=10)
print("\\nBest matches for Qwen PCs against Llama:")
ql_best = [r for r in best_matches if r["model_a"] == "qwen" and r["model_b"] == "llama"]
table(ql_best, ["pc_a", "best_matching_pc_b", "pearson_r", "spearman_r", "matched_role_count"], limit=10)
print("\\nCluster similarity metrics:")
metric_rows = cluster_metrics.get("cluster_similarity_metrics", []) if cluster_metrics else []
table(metric_rows, ["model_pair", "matched_role_count", "kmeans_top3_ari", "kmeans_top3_nmi", "kmeans_top5_ari", "kmeans_top5_nmi"], limit=10)
'''),
    md("**Cross-model interpretation note.** The table above is a local coordinate/best-match diagnostic from this reanalysis, not the same measurement as Lu et al.'s published role-composition comparison. PCA axes can differ by sign, index, and rotation inside a shared low-dimensional subspace, so a same-index correlation is not by itself the whole cross-model story. The cautious report-level claim is that PC1 / the Assistant Axis has the strongest cross-model support in the public paper, and that these diagnostics show substantial shared low-dimensional structure while requiring stronger model-local caveats for later PCs."),
    md("## N03. PC1 Interpretation\n\nQuestion: what does PC1 separate in Qwen role geometry?\n\nData loaded: Qwen role PCA coordinates from public geometry.\n\nMethod: rank roles by PC1 and inspect endpoint examples.\n\nResult shown: high-PC1 roles concentrate around evaluator/procedural/correctness pressure; low-PC1 roles are more open, symbolic, expressive, or possibility-rich.\n\nCaveat: endpoint labels are evidence for the forcing-function interpretation, not the interpretation itself."),
    code('''
top_pc1, bottom_pc1 = top_bottom(roles_df, "pc1", 15)
print("Top PC1 roles:")
table(top_pc1, ["role", "cluster", "pc1", "pc2", "pc3"], limit=15)
print("\\nBottom PC1 roles:")
table(bottom_pc1, ["role", "cluster", "pc1", "pc2", "pc3"], limit=15)
safe_plot_pc_scatter(roles_df, "pc1", "pc2", labels=["assistant", "auditor", "validator", "poet", "bard", "oracle", "demon"], out_name="qwen_pc1_pc2_key_roles.png")
'''),
    md("## N04. PC2 Interpretation\n\nQuestion: does PC2 separate situated/formative/impressionable roles from integrated/stable/durable roles when PC1 is muted or cluster-conditioned?\n\nData loaded: muted-PC1 PC2 extremes and cluster-conditioned PC2 diagnostic outputs.\n\nMethod: display muted-PC1 extremes, diagnostic examples, and expected-direction pass rates.\n\nResult shown: partial support, with important counterexamples.\n\nCaveat: PC2 remains provisional, Qwen-local, and complicated by shapeshifter/chameleon/elder."),
    code('''
muted = load_csv("research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_top_bottom.csv")
diag = load_csv("research/outputs/pc2_cluster_conditioned_extremes/pc2_diagnostic_roles_table.csv")
checks = load_csv("research/outputs/pc2_cluster_conditioned_extremes/pc2_expected_direction_checks.csv")
print("Muted-PC1 PC2 extremes:")
table(muted, ["extreme_group", "extreme_rank", "role", "cluster", "pc1", "pc2", "pc3"], limit=20)
focus = {"patient", "amateur", "tree", "hive", "philosopher", "shapeshifter", "chameleon", "elder"}
print("\\nDiagnostic roles:")
table([r for r in diag if r.get("persona") in focus], ["persona", "cluster", "pc1", "pc2", "global_pc2_rank_desc", "cluster_pc2_rank_desc", "pc2_side_global", "pc2_side_cluster"], limit=20)
global_pass = sum(r.get("global_pass") == "True" for r in checks)
cluster_pass = sum(r.get("cluster_pass") == "True" for r in checks)
print(f"Expected-direction checks: global {global_pass}/{len(checks)}, cluster-relative {cluster_pass}/{len(checks)}")
table(checks, ["persona", "expected_pc2_side", "actual_global_side", "actual_cluster_side", "global_pass", "cluster_pass", "caveat"], limit=12)
'''),
    md("## N05. PC3 Interpretation\n\nQuestion: does PC3 track perturbation/intervention versus stabilization/repair?\n\nData loaded: PC3 validation stats and Qwen role geometry.\n\nMethod: display validation correlations and top/bottom PC3 role rankings.\n\nResult shown: PC3 has a meaningful perturbation/stabilization signal and is not reducible to moral valence.\n\nCaveat: PC3 is weaker cross-model and the rubric scores are deterministic rather than independent human ratings."),
    code('''
pc3_stats = load_json("research/outputs/pc3_validation/pc3_validation_stats.json")
global_stats = pc3_stats.get("global", {}) if pc3_stats else {}
pc3_metric_rows = [
    {"metric": "global Pearson r", "value": global_stats.get("pearson", {}).get("r"), "p": global_stats.get("pearson", {}).get("p")},
    {"metric": "global Spearman r", "value": global_stats.get("spearman", {}).get("r"), "p": global_stats.get("spearman", {}).get("p")},
    {"metric": "within-cluster pairwise accuracy", "value": global_stats.get("pairwise_accuracy_within_cluster", {}).get("accuracy"), "p": ""},
]
partial = pc3_stats.get("partial_controlling_for_cluster", {}) if pc3_stats else {}
if partial:
    pearson = partial.get("pearson", {})
    pc3_metric_rows.append({"metric": "cluster-controlled Pearson r", "value": pearson.get("r"), "p": pearson.get("p", "")})
table(pc3_metric_rows, ["metric", "value", "p"], limit=10)
top_pc3, bottom_pc3 = top_bottom(roles_df, "pc3", 15)
print("\\nTop PC3 roles:")
table(top_pc3, ["role", "cluster", "pc1", "pc2", "pc3"], limit=15)
print("\\nBottom PC3 roles:")
table(bottom_pc3, ["role", "cluster", "pc1", "pc2", "pc3"], limit=15)
safe_plot_pc_scatter(roles_df, "pc2", "pc3", labels=["auditor", "debugger", "skeptic", "caregiver", "healer", "mediator", "demon"], out_name="qwen_pc2_pc3_key_roles.png")
'''),
    md("## N06. Trait/Persona Relationship\n\nQuestion: how much of persona geometry is recoverable from trait-vector relationships?\n\nData loaded: trait-persona prediction stats and trait-space PCA interpretation stats.\n\nMethod: display vector-space verification, prediction metrics, and trait-only PCA alignment values.\n\nResult shown: trait profiles strongly reconstruct persona PCs, but trait-only PCA does not collapse persona geometry into a single trait PCA explanation.\n\nCaveat: same-space reconstruction supports layered geometry, not psychological ontology."),
    md("**Reading the trait metrics.** High-dimensional persona-to-trait cosine profiles contain enough information to reconstruct persona PC coordinates, but this does not mean traits are the causal basis or psychological ontology of persona geometry. The trait-only PCA result is the important caveat: trait PC1 partially aligns with persona PC1, while trait PC2/PC3 do not cleanly align with persona PC2/PC3. That pattern supports a layered-geometry interpretation rather than reducing persona space to trait PCA.\n\n**Count clarification.** The public role-vector extraction recipe uses 5 positive role instructions x 240 shared extraction questions = 1,200 candidate rollouts per role before filtering and averaging. The `64 stored vectors` metadata below refers to the tensor/shard representation in the local vector artifact, not to the original rollout count."),
    code('''
trait_pred = load_json("research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json")
trait_space = load_json("research/outputs/trait_space_interpretation/trait_space_validation_stats.json")
if trait_pred:
    print("Vector space:", trait_pred.get("vector_space", {}))
    pred_rows = []
    for pc, models in trait_pred.get("models", {}).items():
        ridge = models.get("ridge", {})
        held = ridge.get("heldout_20_percent", {})
        cv = ridge.get("five_fold_cv", {})
        pred_rows.append({"pc": pc, "ridge_5fold_r2": cv.get("r2"), "ridge_heldout_r2": held.get("r2"), "heldout_pearson": held.get("pearson"), "heldout_spearman": held.get("spearman")})
    print("\\nTrait-profile cosine -> persona PC ridge metrics:")
    table(pred_rows, ["pc", "ridge_5fold_r2", "ridge_heldout_r2", "heldout_pearson", "heldout_spearman"], limit=10)
if trait_space:
    print("\\nTrait-only PCA explained variance:")
    print(trait_space.get("trait_pca_explained_variance", {}))
    print("\\nPersona/trait PC direction cosines:")
    print(trait_space.get("persona_trait_pc_direction_cosines", {}))
    print("\\nBest trait PC to persona loading match:")
    print(trait_space.get("best_trait_pc_to_persona_loading_match", {}))
'''),
    md("## N07. Prediction-Improvement Sequence\n\nQuestion: which predictive or explanatory improvement claims are traceable enough to show in the core walkthrough?\n\nData loaded: canonical claims traceability table and forecasting/model-comparison outputs.\n\nMethod: filter traceability rows for prediction/model/R2 claims and show status.\n\nResult shown: traceable claims can be used; unverified remembered numbers remain excluded.\n\nCaveat: this section intentionally avoids kitchen-sink exploration and does not backfill missing numbers from chat memory."),
    code('''
trace_rows = claim_trace
keywords = ("r2", "predict", "forecast", "semantic", "procedural", "big five", "svd", "model")
prediction_claims = [r for r in trace_rows if any(k in " ".join(str(v).lower() for v in r.values()) for k in keywords)]
print("Prediction-related traceability rows:")
table(prediction_claims, ["claim_or_number", "value", "source_file", "status", "notes"], limit=20)
optional_or_not_core = [r for r in trace_rows if r.get("status") not in {"verified", "canonical"}]
print("\\nOptional or not-yet-core rows:")
table(optional_or_not_core, ["claim_or_number", "value", "status", "notes"], limit=20)
'''),
    md("## N08. Prompt-to-Geometry Forecasting Baseline\n\nQuestion: can prompt text forecast intended persona/trait geometry before any H100 response-state validation?\n\nData loaded: prompt-to-geometry forecasting results and model comparison table.\n\nMethod: display best held-out role/trait results and the top held-out model-comparison rows.\n\nResult shown: text-only forecasting is promising as an intended-address predictor.\n\nCaveat: this is not evidence that predicted addresses match measured response activations on novel prompts; H100 validation is deferred."),
    code('''
forecast = load_json("research/outputs/prompt_to_geometry_forecasting/forecasting_results.json")
model_cmp = load_csv("research/outputs/prompt_to_geometry_forecasting/forecasting_model_comparison.csv")
if forecast:
    print("Forecasting dataset counts:", {k: forecast.get(k) for k in ["dataset_rows", "trait_count", "role_count", "trait_holdout_count", "role_holdout_count"]})
    print("\\nBest trait heldout:")
    print(json.dumps(forecast.get("best_trait_heldout", {}), indent=2)[:1200])
    print("\\nBest role heldout:")
    print(json.dumps(forecast.get("best_role_heldout", {}), indent=2)[:1200])
heldout = [r for r in model_cmp if r.get("split") == "heldout"]
def mean_r2(row): return fnum(row.get("mean_R2"), -999)
heldout_sorted = sorted(heldout, key=mean_r2, reverse=True)
print("\\nTop held-out model comparison rows:")
table(heldout_sorted, ["concept_type", "variant", "model", "PC1_R2", "PC2_R2", "PC3_R2", "mean_R2"], limit=12)
'''),
    md("## N09. Main Visualization Tool\n\nQuestion: where is the canonical local persona geometry viewer?\n\nData loaded: file-existence check for `research/visualizations/persona_geometry_explorer.html`.\n\nMethod: print path and size.\n\nResult shown: the main viewer path for local inspection.\n\nCaveat: H100 forecast-observed arrow viewers are excluded from this notebook and no visualization files are modified."),
    code('''
viewer = REPO_ROOT / "research/visualizations/persona_geometry_explorer.html"
print("Main viewer exists:", viewer.exists())
if viewer.exists():
    print("Relative path:", viewer.relative_to(REPO_ROOT))
    print("Size bytes:", viewer.stat().st_size)
print("Excluded from this notebook: H100 forecast-observed arrow viewers and prompt-battery visualizations.")
'''),
    md("## N10. Summary of Claims, Confidence, and Next Tests\n\nQuestion: what should carry forward into the technical report, and what remains deferred?\n\nData loaded: this notebook's traceability summary.\n\nMethod: build a compact claims table.\n\nResult shown: report-ready claims, confidence, caveats, and next tests.\n\nCaveat: H100 validation, extraction-boundary tests, and within-role activation clouds remain outside this pre-H100 walkthrough."),
    code('''
summary_claims = [
    {"claim": "Public persona geometry and prompt artifacts are reconstructable enough for a reproducible pre-H100 walkthrough.", "evidence_artifact": "geometry_viz_data.json; prompt inventories; role rollout audit", "confidence": "high", "caveat": "No public generated responses or judge masks.", "next_test": "Instance-level 5x240 forecaster if target role is selected."},
    {"claim": "PC1 is best read as convergence pressure versus degrees of freedom.", "evidence_artifact": "Qwen PC1 rankings; forcing-function note; public Assistant Axis cross-model result", "confidence": "high", "caveat": "Interpretive, not causal proof; same-index cross-model PCA coordinates can rotate or swap signs/indices.", "next_test": "Prompt-level judge rubric validation."},
    {"claim": "PC2 is situated/formative/impressionable versus integrated/stable, provisionally.", "evidence_artifact": "muted-PC1 and cluster-conditioned PC2 diagnostics", "confidence": "medium-low", "caveat": "Shapeshifter/chameleon/elder counterexamples; cross-model rotation.", "next_test": "Blinded within-cluster matched-pair PC2 study."},
    {"claim": "PC3 tracks perturbation/intervention versus stabilization/repair.", "evidence_artifact": "pc3_validation_stats.json", "confidence": "medium", "caveat": "Cross-model PC3 weaker; deterministic rubric.", "next_test": "Independent rater validation and response-state tests."},
    {"claim": "Trait profiles strongly reconstruct persona PCs but do not replace persona PCA.", "evidence_artifact": "trait_persona_prediction; trait_space_interpretation", "confidence": "high for reconstruction, medium for interpretation", "caveat": "Same-space reconstruction is not psychological ontology; trait-only PCA weakly aligns with persona PC2/PC3.", "next_test": "Layered model ablations."},
    {"claim": "Prompt-to-geometry forecasting is a useful but optional pre-H100 intended-address baseline.", "evidence_artifact": "prompt_to_geometry_forecasting", "confidence": "medium", "caveat": "Not execution-time response activation validation; include as extension if the clean repo keeps forecasting.", "next_test": "Corrected extraction-boundary validation before broad H100 interpretation."},
]
table(summary_claims, ["claim", "confidence", "evidence_artifact", "caveat", "next_test"], limit=20)
print("\\nDeferred work: D01 hook-vs-hidden-state boundary test; within-role activation cloud/variance study; judge-filter centroid comparison; instance-level 5x240 forecaster; corrected broad validation only if needed.")
'''),
]


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build_notebook() -> dict:
    return {
        "cells": NOTEBOOK_CELLS,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
            "paper15": {
                "purpose": "Core pre-H100 executable walkthrough skeleton",
                "generated_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
                "excludes": ["H100 validation outputs", "prompt batteries", "RunPod logs", "extraction-boundary diagnostics"],
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def execute_code_cells(notebook: dict) -> dict:
    namespace: dict = {"__name__": "__notebook_check__"}
    executed = 0
    errors: list[dict] = []
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = cell["source"]
        try:
            ast.parse(source)
            exec(compile(source, f"{NOTEBOOK_PATH.name}:cell{index}", "exec"), namespace)
            executed += 1
        except Exception as exc:  # noqa: BLE001 - report all notebook-check errors.
            errors.append({
                "cell_index": index,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(limit=4),
            })
            break
    return {
        "execution_method": "plain_python_exec_over_code_cells",
        "jupyter_available": False,
        "executed_code_cells": executed,
        "error_count": len(errors),
        "errors": errors,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)

    dependency_rows = []
    for section, input_file, role, source_dir, caveat in DEPENDENCIES:
        dependency_rows.append({
            "notebook_section": section,
            "input_file": input_file,
            "exists": str((REPO_ROOT / input_file).exists()),
            "role_in_notebook": role,
            "source_output_dir": source_dir,
            "caveat": caveat,
        })
    write_csv(
        OUT_DIR / "notebook_data_dependency_table.csv",
        dependency_rows,
        ["notebook_section", "input_file", "exists", "role_in_notebook", "source_output_dir", "caveat"],
    )

    claim_rows = [
        {
            "claim": claim,
            "notebook_section": section,
            "supporting_file": supporting_file,
            "metric_or_table": metric,
            "canonical_status": status,
            "caveat": caveat,
        }
        for claim, section, supporting_file, metric, status, caveat in CLAIMS
    ]
    write_csv(
        OUT_DIR / "notebook_claim_traceability_table.csv",
        claim_rows,
        ["claim", "notebook_section", "supporting_file", "metric_or_table", "canonical_status", "caveat"],
    )

    notebook = build_notebook()
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    run_status = execute_code_cells(notebook)
    run_status.update({
        "notebook_path": str(NOTEBOOK_PATH.relative_to(REPO_ROOT)),
        "generated_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "missing_dependency_files": [r["input_file"] for r in dependency_rows if r["exists"] != "True"],
        "optional_python_dependencies_missing": ["jupyter", "nbformat", "pandas", "matplotlib", "IPython"],
    })
    (OUT_DIR / "notebook_run_status.json").write_text(json.dumps(run_status, indent=2) + "\n", encoding="utf-8")

    sections = [cell["source"].splitlines()[0].lstrip("# ").strip() for cell in NOTEBOOK_CELLS if cell["cell_type"] == "markdown" and cell["source"].lstrip().startswith("## ")]
    missing_files = [r["input_file"] for r in dependency_rows if r["exists"] != "True"]
    missing_lines = [f"- `{p}`" for p in missing_files] if missing_files else ["- None among required notebook input files."]
    report = [
        "# Paper 1.5 Notebook Build Report",
        "",
        f"Generated UTC: {run_status['generated_utc']}",
        f"Notebook path: `{NOTEBOOK_PATH.relative_to(REPO_ROOT)}`",
        "",
        "## Sections Created",
        "",
        *[f"- {s}" for s in sections],
        "",
        "## Data Files Referenced",
        "",
        *[f"- `{r['input_file']}` — exists={r['exists']} — {r['role_in_notebook']}" for r in dependency_rows],
        "",
        "## Missing Files or Unresolved Dependencies",
        "",
        *missing_lines,
        "",
        "## Placeholders",
        "",
        "- Plot cells are guarded: figures are skipped when `matplotlib` is unavailable.",
        "- The notebook uses standard-library tables instead of pandas DataFrames so it can run in a minimal Python kernel.",
        "- H100 validation, prompt-battery generation, extraction-boundary diagnostics, and RunPod materials are intentionally deferred.",
        "",
        "## Execution Status",
        "",
        f"- Execution method: `{run_status['execution_method']}`",
        f"- Executed code cells: {run_status['executed_code_cells']}",
        f"- Error count: {run_status['error_count']}",
        "- Jupyter execution: not attempted because `jupyter`, `nbformat`, and `nbclient` are not installed in this local Python environment.",
    ]
    if run_status["errors"]:
        report.extend(["", "## Execution Errors", ""])
        for err in run_status["errors"]:
            report.append(f"- Cell {err['cell_index']}: {err['error_type']}: {err['error']}")
    (OUT_DIR / "notebook_build_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return 1 if run_status["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
