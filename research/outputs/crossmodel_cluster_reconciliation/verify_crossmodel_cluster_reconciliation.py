#!/usr/bin/env python3
"""Deterministic verification for AA-12 follow-up 3."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import hypergeom
from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score, normalized_mutual_info_score


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "research/outputs/cross_resolution_profile_banks/model"
MODELS = ("qwen", "llama", "gemma")
PAIRS = (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma"))
KS = tuple(range(4, 11))
HASHES = {
    "qwen": "2c4aee82f6ed7499401e45174b7e354bb4a4e09ff4600536c5534dc48a6a2f0d",
    "llama": "e4e74cd915c3490fd7e4adbddf8bb38e4058dc41e104acf7ab03a8a2285aa86f",
    "gemma": "4df15ca4048a26a7b5ac3c93885baa1f9f0ffe866e2282c83d4c0520cf38d2d1",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    checks = []

    def check(name: str, condition: bool, detail=""):
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": str(detail)})

    startup = json.loads((HERE / "startup_verification_record.json").read_text())
    check("startup passed", startup["status"] == "PASS")
    check("four exact startup URLs checked", len(startup["checks"]) == 4 and all(x["http_status"] == 200 for x in startup["checks"]))
    check("visible startup metadata checked", all(x.get("visible_metadata_match", True) for x in startup["checks"]))
    check("canonical navigation consulted", len(startup["canonical_navigation_consulted"]) == 6)
    check("method preregistration exists", (HERE / "analysis_preregistration.md").exists())
    method_text = (HERE / "analysis_preregistration.md").read_text()
    check("AMI primary metric frozen", "Primary metric: adjusted mutual information" in method_text)
    check("K search frozen 4 through 10", "every integer from 4 through 10" in method_text)
    check("5000 permutations frozen", "5,000 deterministic permutations" in method_text)
    check("permutation seed frozen", "2026091303" in method_text)
    check("quality threshold frozen", "at least 0.70" in method_text)
    check("split merge allowed", "one-to-one, split, merge" in method_text)
    check("anti-transitivity rule frozen", "prevent unsupported transitive chaining" in method_text)

    memberships = {}
    common_roles = None
    for model in MODELS:
        path = SOURCE / model / "memberships.csv"
        check(f"{model} frozen membership hash", sha(path) == HASHES[model], sha(path))
        df = pd.read_csv(path)
        memberships[model] = df
        check(f"{model} has K4-K10", sorted(df.K.unique()) == list(KS))
        check(f"{model} has 275 roles per K", df.groupby("K").opaque_role_id.nunique().eq(275).all())
        check(f"{model} has no duplicate K-role", not df.duplicated(["K", "opaque_role_id"]).any())
        roles = set(df.opaque_role_id)
        common_roles = roles if common_roles is None else common_roles
        check(f"{model} shared role inventory", roles == common_roles)
    check("same exact 275 roles across models", len(common_roles) == 275)

    pairwise = pd.read_csv(HERE / "pairwise_k_agreement.csv")
    triples = pd.read_csv(HERE / "triple_k_agreement.csv")
    quality = pd.read_csv(HERE / "quality_constrained_agreement.csv")
    null = pd.read_csv(HERE / "permutation_max_null.csv")
    summary = json.loads((HERE / "partition_agreement_summary.json").read_text())
    check("all 147 pairwise K cells present", len(pairwise) == 147)
    for a, b in PAIRS:
        sub = pairwise[(pairwise.model_a == a) & (pairwise.model_b == b)]
        check(f"{a}-{b} has 49 K cells", len(sub) == 49 and not sub.duplicated(["K_a", "K_b"]).any())
    check("all 343 K triples present", len(triples) == 343 and not triples.duplicated(["K_qwen", "K_llama", "K_gemma"]).any())
    check("quality sensitivity nonempty", len(quality) > 0 and quality.quality_constrained.all())
    check("5000 permutation maxima present", len(null) == 5000 and null.permutation.nunique() == 5000)
    check("null preserves one maximum per model pair", {"qwen_llama_max_ami", "qwen_gemma_max_ami", "llama_gemma_max_ami"}.issubset(null.columns))
    check("triple maximum null present", "triple_max_mean_ami" in null.columns)
    check("best triple Q6 L9 G6", tuple(triples.iloc[0][["K_qwen", "K_llama", "K_gemma"]].astype(int)) == (6, 9, 6))
    check("quality best equals global best", tuple(quality.iloc[0][["K_qwen", "K_llama", "K_gemma"]].astype(int)) == (6, 9, 6))
    check("triple score recomputes", np.isclose(triples.iloc[0].mean_pairwise_ami, np.mean(triples.iloc[0][["qwen_llama_ami", "qwen_gemma_ami", "llama_gemma_ami"]].astype(float))))
    p = (1 + (null.triple_max_mean_ami >= triples.iloc[0].mean_pairwise_ami - 1e-15).sum()) / 5001
    check("search-adjusted p recomputes", np.isclose(p, summary["triple_search_adjusted_p"]), p)
    check("search-adjusted p is significant", p <= .05, p)
    check("near-best triple ridge recorded", triples.near_best.sum() == 8 and summary["triple_broad_ridge"])

    role_order = sorted(common_roles)
    for row in [pairwise.iloc[0], pairwise.iloc[48], pairwise.iloc[98], pairwise.iloc[146]]:
        da = memberships[row.model_a]
        db = memberships[row.model_b]
        ma = dict(zip(da[da.K == row.K_a].opaque_role_id, da[da.K == row.K_a].profile_id))
        mb = dict(zip(db[db.K == row.K_b].opaque_role_id, db[db.K == row.K_b].profile_id))
        la, lb = [ma[r] for r in role_order], [mb[r] for r in role_order]
        check(f"AMI recomputes {row.model_a}{int(row.K_a)}-{row.model_b}{int(row.K_b)}", np.isclose(row.ami, adjusted_mutual_info_score(la, lb, average_method="arithmetic")))
        check(f"ARI recomputes {row.model_a}{int(row.K_a)}-{row.model_b}{int(row.K_b)}", np.isclose(row.ari, adjusted_rand_score(la, lb)))
        check(f"NMI recomputes {row.model_a}{int(row.K_a)}-{row.model_b}{int(row.K_b)}", np.isclose(row.nmi, normalized_mutual_info_score(la, lb, average_method="arithmetic")))

    overlaps = pd.read_csv(HERE / "cluster_overlap_matrices.csv")
    edges = pd.read_csv(HERE / "cluster_overlap_edges.csv")
    persistence = pd.read_csv(HERE / "cross_resolution_persistence.csv")
    tiny = pd.read_csv(HERE / "tiny_cluster_audit.csv")
    check("all 7203 cluster pairs present", len(overlaps) == 7203)
    check("all 147 overlap cells present", overlaps.groupby(["model_a", "model_b", "K_a", "K_b"]).ngroups == 147)
    check("overlap statistics finite", np.isfinite(overlaps[["jaccard", "overlap_coefficient", "hypergeom_p", "hypergeom_q"]]).all().all())
    sample = overlaps.iloc[137]
    check("sample expected overlap recomputes", np.isclose(sample.expected_overlap, sample.size_a * sample.size_b / 275))
    check("sample hypergeometric p recomputes", np.isclose(sample.hypergeom_p, hypergeom.sf(sample.intersection_count - 1, 275, sample.size_a, sample.size_b)))
    check("strong edge subset exact", len(edges) == overlaps.strong_edge.sum() == 961)
    check("all edges satisfy q threshold", edges.hypergeom_q.le(.01 + 1e-15).all())
    check("persistence row for every edge", len(persistence) == len(edges))
    recomputed_tier = np.where(
        (persistence.valid_neighborhood_cells >= 4) & (persistence.persistence_score >= .75 - 1e-12), "high",
        np.where((persistence.valid_neighborhood_cells >= 4) & (persistence.persistence_score >= .50 - 1e-12), "moderate", "isolated"),
    )
    check("persistence tiers recompute", np.array_equal(recomputed_tier, persistence.persistence_tier.to_numpy()))
    check("tiny audit has 24 unique tiny clusters", tiny[["model", "K", "profile_id"]].drop_duplicates().shape[0] == 24)
    check("tiny audit covers both other models and every K", len(tiny) == 24 * 2 * 7)
    check("tiny audit contains semantic names only post-freeze", tiny.role_names.notna().all())

    trait_edges = pd.read_csv(HERE / "cluster_trait_profile_similarity.csv")
    families = pd.read_csv(HERE / "candidate_consensus_families.csv")
    family_roles = pd.read_csv(HERE / "consensus_family_roles.csv")
    family_traits = pd.read_csv(HERE / "consensus_family_trait_profiles.csv")
    consensus = json.loads((HERE / "consensus_summary.json").read_text())
    check("trait confirmation covers every strong edge", len(trait_edges) == len(edges))
    check("trait evidence labeled secondary", trait_edges.evidence_role.eq("secondary same-activation-space confirmation").all())
    check("trait correlations bounded", trait_edges[["pearson_240_traits", "spearman_240_traits", "centered_cosine_240_traits"]].abs().le(1 + 1e-12).all().all())
    check("five candidate components", len(families) == 5)
    check("four all-three families", families.model_count.eq(3).sum() == 4)
    check("direct support complete", families.direct_all_represented_model_pairs.all())
    check("majority coverage 220 roles", family_roles[family_roles.model_support_count >= 2].opaque_role_id.nunique() == 220)
    ambiguous = family_roles[family_roles.model_support_count >= 2].groupby("opaque_role_id").consensus_family_id.nunique().gt(1).sum()
    check("no ambiguous majority roles", ambiguous == 0)
    check("consensus candidate status established", consensus["status"] == "ESTABLISHED_CANDIDATE_SET")
    check("family traits have 240 per family-model", family_traits.groupby(["consensus_family_id", "model"]).trait.nunique().eq(240).all())
    check("trait profiles labeled secondary", family_traits.evidence_role.eq("secondary same-activation-space description").all())

    # Commit ordering: method -> partition -> cluster -> trait -> semantic.
    commit_chain = [
        "2a38f67038b4bd55c9ff9f9ec405eb1761d50348",
        "4b16aac0409de83972ee9fe688ce959ff7ffe45b",
        "93aa3908aa26cf3c6adb814a427d047fc594e741",
        "83e0e545041b5ae9f8db0c1983fde39b610f0c3f",
        "0e868aa32fa0c09bfb5044ab31713f6ef0f34855",
    ]
    check("freeze commits exist", all(git("cat-file", "-t", c) == "commit" for c in commit_chain))
    check("freeze commit ordering", all(subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=REPO).returncode == 0 for a, b in zip(commit_chain, commit_chain[1:])))

    scripts = "\n".join((HERE / fn).read_text().lower() for fn in [
        "run_partition_agreement.py", "run_cluster_correspondence.py", "run_trait_consensus.py"
    ])
    check("no human source paths in numerical scripts", "sapa_partial_response" not in scripts and "human_cross_resolution" not in scripts)
    check("no inference libraries", "transformers" not in scripts and "openai" not in scripts)
    check("no GPU or RunPod operations", "cuda" not in scripts and "runpod" not in scripts)
    check("no human-model metric output", not any("human" in p.name.lower() for p in HERE.iterdir()))
    check("no respondent-level output", not any("respondent" in p.name.lower() for p in HERE.iterdir()))

    required_figures = [
        "qwen_llama_ami_heatmap.png", "qwen_gemma_ami_heatmap.png", "llama_gemma_ami_heatmap.png",
        "triple_agreement_ranked.png", "observed_vs_permutation_max_null.png",
        "anchor_qwen_llama_cluster_overlap.png", "anchor_qwen_gemma_cluster_overlap.png",
        "anchor_llama_gemma_cluster_overlap.png", "anchor_cluster_correspondence_graph.png",
        "tiny_cluster_membership_comparison.png", "consensus_family_trait_heatmap.png",
    ]
    check("all required figures present", all((HERE / "figures" / x).stat().st_size > 1000 for x in required_figures))
    check("primary report exists", (HERE / "crossmodel_cluster_reconciliation_report.md").exists())
    check("semantic summary exists", (HERE / "semantic_consensus_summary.md").exists())

    if args.rerun:
        core = [
            "pairwise_k_agreement.csv", "triple_k_agreement.csv", "quality_constrained_agreement.csv",
            "permutation_max_null.csv", "cluster_overlap_matrices.csv", "cluster_overlap_edges.csv",
            "cross_resolution_persistence.csv", "tiny_cluster_audit_opaque.csv",
            "cluster_trait_profile_similarity.csv", "candidate_consensus_families.csv",
            "consensus_family_roles_opaque.csv", "consensus_family_trait_profiles.csv",
        ]
        before = {x: sha(HERE / x) for x in core}
        for script in ["run_partition_agreement.py", "run_cluster_correspondence.py", "run_trait_consensus.py", "build_semantic_outputs.py"]:
            subprocess.run([str(REPO.parent / "assistant-axis/.venv/bin/python"), str(HERE / script)], cwd=REPO, check=True, capture_output=True, text=True)
        after = {x: sha(HERE / x) for x in core}
        check("deterministic full numerical rerun", before == after)

    worktree = git("status", "--porcelain")
    check("working tree clean at verification start", worktree == "", worktree)
    failures = [x for x in checks if x["status"] != "PASS"]
    report = {
        "status": "PASS" if not failures else "FAIL",
        "model_used": "GPT-5.5",
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "checks": checks,
        "boundaries": {
            "human_data_loaded": False,
            "sapa_artifact_loaded": False,
            "human_model_matching": False,
            "reclustering": False,
            "new_model_inference": False,
            "activation_extraction": False,
            "external_model_api": False,
            "gpu": False,
            "runpod": False,
        },
    }
    (HERE / "verification_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "passed": report["checks_passed"], "total": report["checks_total"]}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
