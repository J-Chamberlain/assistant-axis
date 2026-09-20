# Executive takeaway

1. **Five best additional distinct concepts: undetermined.** The feasibility gate failed before candidate selection; no concepts were ranked.
2. **Smallest useful set: undetermined.** The k=1–8 table contains explicit not-run statuses, not a performance curve.
3. **Broad-profile improvement: not estimated.** The existing broad SAPA target cannot be reused as a valid frozen trait profile: its scoring implementation fails its reverse-scoring and missingness definitions.
4. **Big Five and HiFWB improvement: not estimated in AA-26.** Earlier outcome results do not answer this broad-profile expansion question.
5. **Concepts justified for later model-side elicitation by this audit: none established.** This is absence of an evaluable ranking, not evidence that all concepts lack value.

The raw human data are **available**, not missing. The missing prerequisite is a valid, fully specified, frozen broad-profile target compatible with the requested leakage exclusions. The user explicitly requires stopping rather than improvising a target when this gate fails. Repairing and refreezing the broad target is the next step; AA-26 does not silently change prior scoring definitions, substitute a narrower outcome, or manufacture rankings.

## Scope and provenance

This CPU-only audit used the existing SAPA V5 responses and documented bridge artifacts. No model inference, activations, model prompts, persona scoring, viewers, RunPod, paid compute, or external data acquisition were used. The analytical agent is Astra (GPT-6), as requested; historical source metadata is preserved unchanged.

Base: `56902f6` on the AA-25 lineage. Branch: `codex/aa26-sapa-profile-information-gain`. The five explicitly requested inputs were inspected in full by the audit script: 240-row crosswalk, 223-row scale inventory (92 administered constructs plus 131 derived keys), 74-row support table, 9,694-row scale-association table, and 74-row Big Five association table. These are aggregate artifacts; none contains respondent-level target profiles or out-of-sample candidate gains.

Startup/state/provenance records identify the broad human-profile work as AA-13. Its artifacts are on the existing `codex/aa13-broad-sapa-pca-wellbeing` branch at immutable commit `045ac766949356ffb31705c69ba677824faf65b8`, rather than in the AA-25 tree. AA-26 reads only its relevant provenance, inventory, scoring implementation, report, and verification blobs. It does not rerun its programs or alter AA-13. Exact source paths, commits, sizes, and hashes are recorded in `source_artifact_inventory.csv`.

The originally recorded acquisition paths no longer exist. Exact standard SAPA dependency paths in registered worktrees locate existing copies in AA-10 and the human-construct bridge worktree. The audit uses the AA-10 copy, supplied as `--data-dir`. All three required raw inputs match their documented hashes:

| Input | SHA256 |
|---|---|
| `sapaTempData696items08dec2013thru26jul2014.tab` | `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6` |
| `superKey696.csv` | `8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49` |
| `ItemInfo696.csv` | `ce280ebf42cd77f3db1955a3027051a74d017ca61da02adf5dbbab11545b1732` |

Only the 696 psychological response columns are retained in memory. The 23,679 source rows are never exported. Aggregate audit tables do not identify respondents.

## Target gate: rejected before fitting

The broadest **previously assembled profile identified in the documented broad-profile analysis** is AA-13's 79 administered-source dimensions, spanning IPIP100, BFAS, HEXACO, QB6, MPQ, IPIPneo, EPQr, and PS. Its full dimension list, source scale identities, item memberships, per-dimension respondent counts, missingness, official-key correspondence, and baseline overlaps are in `target_dimension_audit.csv`. No dimensions are accepted as the AA-26 target; the table documents the rejected target rather than a new analysis freeze.

The 79 dimensions use 610 of the 696 items. AA-13's manifest and analysis freeze require at least two observed items per scale and at least 2% coverage. Its inventory instead says “>=50% observed.” The implementation computes a mean whenever at least one item is present and uses the two-item count only to decide whether to retain a scale globally; it never masks the one-item means before PCA. AA-26 independently reproduces every one of the 79 published two-item coverage counts. Nevertheless, **636,832 one-item respondent-by-scale cells** enter the saved scoring implementation. There are 917 complete 79-dimensional profiles under the implementation's one-item availability, versus **35** under the documented two-item rule; the median respondent has **28/79** two-item dimensions. Complete cases are diagnostic only, not a proposed analysis sample. Neither median missingness nor the small complete-case count alone proves a missing-aware analysis impossible.

The larger validity problem is directionality. The primary scorer compares administered source IDs such as `IPIP100:B5:A` against derived key names such as `IPIP100agree`. **Zero** source IDs match the reverse-key namespace. The follow-up scorer averages the raw items without reverse-keying at all. For **78/79 dimensions**, AA-26 finds exactly one official derived key with the same item membership, and all 78 require at least one reversal. For example, the 20-item Agreeableness scale requires reversing `q_140;q_146;q_195;q_200;q_838;q_1163`; the old scorer reverses none. The exact evidence is in `reverse_scoring_evidence.csv`.

The remaining source dimension, `IPIP100_B5_E`, includes `q_55`, while the official `IPIP100extra` key has 19 items and omits it. Thus blindly replacing every source scale with an official key would also change one dimension's item membership. The available keys support a repair of much of this profile, but that would be a corrected/refrozen profile, **not reproduction of the existing frozen target**. This audit does not claim that a valid future profile is mathematically unreconstructable or that new human data are needed.

The saved PCA summaries are not an alternative respondent-level target: they inherit the same input scoring and missingness defects, and aggregate loadings/correlations cannot replace observed respondent outcomes for held-out reconstruction. A profile using all 131 official keys would be a different target definition; its union covers all 696 items, leaving zero unused target-disjoint item predictors. We did not silently substitute it.

## Current bridge and leakage audit

The current operational bridge is AA-19's frozen **41 unique-source, future-safe direct proxies**, reused in AA-22/23, with 90 unique items. `baseline_predictor_audit.csv` preserves its item lists and direction signs. The older psychometric tier comprises 45 direct labels using 96 unique items and is documented separately as a historical baseline sensitivity; it is not silently substituted for the operational bridge. The 29 close mappings are not part of the primary baseline.

Against the rejected 79-dimensional target, **82/90** current-bridge items, **85/96** historical direct-bridge items, and **99/99** official Big Five items overlap target items. All 99 Big Five predictor items are in the target, so a naive comparison would partly reconstruct the same observed answers. This is a separate mechanical-overlap concern from held-out respondent leakage: holding out respondents does not remove shared-item content. The report does not interpret it as broad trait information gain.

There are 86 items outside the AA-13 target and 78 outside both that target and current bridge plus Big Five, **before** HiFWB exclusion, coverage, ambiguity, and redundancy checks. These are availability counts, not an eligible or ranked candidate pool. A replacement target must state its policy for baseline–target overlap as well as exclude all target items from new candidates; the scored dimensions cannot change depending on which candidate is tested.

The four requested comparisons are enumerated in `profile_reconstruction_comparison.csv`, with blank metrics and `NOT_RUN_TARGET_GATE_FAILED`: current bridge only, Big Five only, current bridge plus Big Five, and current bridge plus Big Five plus selected candidates. No Big Five self-prediction score or previous HiFWB result is substituted for a broad-profile comparison.

## Selection protocol status

No candidate pool, redundancy grouping, split, estimator, or predictor selection was fitted. No in-sample correlation was used to rank candidates. Candidate ranking, selections, incremental gains, and stability CSVs are schema-only; blank values mean **not evaluated**, not zero effect. `minimal_set_curve.csv` enumerates k=1–8 with the same explicit not-run status.

For a later run, the proposed primary tolerance is **0.01 absolute macro-average held-out profile R²** from the best k=1–8 set, with 0.005 and 0.02 sensitivity tolerances. This is documented before any fitting, but no minimal-set conclusion is licensed here. A later freeze must specify equal weighting over fixed target dimensions, observed-target scoring, training-only scaling/imputation, nested family selection and regularization, a common respondent comparison rule, distinctness by source identity and training-fold residual correlation (proposed |r|>=0.80, sensitivity 0.70/0.90), and split/bootstrap stability. At most one representative from each redundant family would enter the primary path. Proposed rules are not represented as an executed experiment.

Big Five reconstruction must withhold its outcome items from bridge/candidate predictors and cannot include the same Big Five measurements as predictors of themselves. HiFWB must use the previously frozen 13-item outcome with all outcome items excluded from predictors. Future model-side elicitation requires stable, distinct human incremental evidence; even a positive future result would not establish representation in models, human-equivalent factors, or causal effects.

## What must exist before resuming

1. A corrected and frozen broad target specification with explicit keyed source membership for every retained dimension, including resolution of `IPIP100_B5_E`/`q_55`, and a single enforced missingness rule. Preserve the old profile as historical evidence.
2. Verified respondent-level reconstruction of that specification from the existing hash-matched source, with per-dimension coverage and no synthetic “complete profiles” treated as observed truth.
3. A fixed item partition and evaluation definition that prevents new-candidate target leakage and explicitly handles the current-bridge/Big Five shared-target content. Any scale-item changes need their own documented target version rather than candidate-specific targets.
4. A pre-fit candidate pool, grouping rule, nested/held-out evaluation and stability plan before ranking or interpreting k and tolerance.

These are missing measurement/evaluation specifications, not a request for fresh model prompts, new survey items, paid compute, or new human acquisition. Under the user's explicit gate, AA-26 ends at this feasibility audit.

## Verification and closeout

Run `run_feasibility_audit.py --data-dir PATH`, then `verify_outputs.py` from this directory or the repository root. The latter checks source hashes and immutable provenance, aggregate count identities, target failure evidence, empty ranking schemas, explicit k=1–8 not-run rows, baseline preservation, no modifications to AA-16–AA-25, and parseable output/navigation records. `verification_report.json` distinguishes successful audit verification from the **blocked scientific analysis**. `artifact_inventory.csv` includes SHA256 hashes for every other file in this output directory; it excludes itself to avoid a recursive hash.

Canonical state, thread continuity, claims, findings, provenance, research index, and navigation records register the blocker. A pre-existing `REPO_FILE_INDEX.csv` corruption (invalid UTF-8 at the AA-25-lineage base, byte-identical to git) was also found during the required navigation update. Navigation repair restores the valid AA-20 index and reconciles subsequent tracked-path changes using git metadata only; it does not inspect unrelated research content. The immutable parent history retains the corrupted version. No sticky note was changed.
