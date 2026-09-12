# Paper 1.5 Content Ledger

Canonical status: active source ledger for Paper 1.5 writing.

Scope: factual evidence ledger only. This is not a paper draft, report, executive summary, or narrative discussion.

Primary ledger sources:

- `research/RESEARCH_STATE.md`
- `research/THREAD_START.md`
- `research/RESEARCH_INDEX.md`
- `research/PROVENANCE_REGISTRY.md`
- `research/CLAIMS_REGISTER.md`
- `research/FINDINGS_LEDGER.md`
- Primary artifacts listed in `research/paper15_content_ledger_artifact_inventory.csv`

## 1. Research Scope

Paper title:

- `Interpreting Persona Activation Geometry`

Research questions:

| ID | Question | Status |
|---|---|---|
| RQ1 | What semantic, trait, procedural, and residual structures explain Qwen persona activation PCA geometry? | active |
| RQ2 | How should PC1, PC2, and PC3 be interpreted under current evidence? | active |
| RQ3 | Which interpretations are supported, tentative, speculative, or rejected? | active |
| RQ4 | Do blinded ratings and no-label elicitation experiments support the working PC interpretations? | active |
| RQ5 | Which evidence belongs in the main Paper 1.5 argument versus appendix or exclusion? | active |
| RQ6 | How many persona PCA components are supported as a strict core, weaker secondary coordinates, or exploratory variation? | active |
| RQ7 | Do externally constrained trait directions recur after aligning model-local PC1-PC6 role-score subspaces? | active; bounded model-only evidence |

Intended contribution:

- Observed: consolidate public/released persona geometry, prompt artifacts, trait/vector overlays, predictive benchmarks, blinded rater studies, and no-label elicitation results into a defensible interpretation of persona activation geometry.
- Inferred: argue for a layered interpretation: semantic topology, same-space trait structure, procedural/operating-mode structure, and residual lexical/developmental/liminal structure.
- Speculative: local activation-cloud and future within-role displacement work may extend the point-estimate interpretation into distributional persona geometry, but that is not the Paper 1.5 core.

Explicit non-goals:

- Do not claim that PC axes are proven causal mechanisms.
- Do not claim that persona geometry validates human psychology.
- Do not treat Big Five-style features as independent psychometric evidence.
- Do not treat same-space trait-vector overlays as independent ratings.
- Do not make H100/A100 forecast-observed validation the core Paper 1.5 result.
- Do not include prompt-battery generation or H100 extraction-boundary debugging in the main paper argument.
- Do not frame adaptive extraction replication as the headline Paper 1.5 contribution.
- Do not treat no-label prompt effects as axis-isolated.

## 2. Methods

| Method | Purpose | Inputs | Outputs | Evidence status |
|---|---|---|---|---|
| Role geometry reconstruction | Recover canonical Qwen role/persona PC coordinates and support geometry inspection. | `research/visualizations/geometry_viz_data.json`; `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv`; released/local Qwen role vectors. | Canonical role PC coordinates; role rankings; cluster membership tables. | established source geometry |
| PCA analysis | Define PC1/PC2/PC3 coordinate system for released role vectors. | Released Qwen role-vector artifacts and canonical PCA tables. | PC coordinates, explained variance, role rankings. | established within project |
| Extended PCA dimensionality audit | Test the full spectrum rather than assuming the original 3D display is the scientific cutoff. | Exact saved 275-role Qwen/Llama/Gemma tensors; established coordinate orientation; Qwen trait matrix and role instructions. | Full rank-274 spectra, thresholds, knees, broken-stick, parallel analysis, bootstrap component/subspace stability, PC4+ interpretation packet, cross-model recurrence controls, PC1-PC10 viewer. | established dimensionality audit; PC1-PC3 strict core, PC4-PC6 supported secondary Qwen coordinates |
| Trait overlays | Inspect same-space role-trait structure without independent psychometric claims. | `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`; `research/outputs/same_space_big_five_overlay/`; trait vectors. | Trait-profile matrices; activation-derived Big Five projections; trait-region overlays. | same-space evidence, not independent rating |
| Qwen trait sparsity and basis-coverage audit | Distinguish compact semantic efficiency from generic high-dimensional reconstruction in the complete 240-trait predictor. | Existing Qwen role/trait tensors, 275 x 240 activation-cosine matrix, canonical PC targets, fixed editorial traits, and fold-local generic controls. | Nested compact selection, feature-budget thresholds, matched random real-trait/isotropic/persona-span controls, trait-span PC coverage, redundancy and norm audits. | mixed evidence: strong compact real-trait advantage plus near-complete high-k basis coverage |
| Externally anchored Big Five audit | Test geometry-blind public-IPIP/SAPA-anchored activation directions and extend the canonical multimodel viewers. | Public-domain IPIP facet keys; reviewed AA-1 SAPA bridge; canonical trait definitions; saved Qwen/Llama/Gemma role and trait vectors. | Four frozen constructions, direction cosines, role-score associations, partial models, sensitivity tables, and integrated ridge/surface modes. | strong same-space Qwen Agreeableness-PC3 component; not independent human validation or universal PC identity |
| Trait-profile PC predictor generalization | Test whether a complete activation-derived trait profile predicts PC1/PC2/PC3 when a persona or fixed Qwen-canonical role family is absent from fitting; compare Qwen, Llama, and Gemma in their own PCA geometries. | Existing 275 x 240 same-model role-trait cosine matrices; canonical/established model-specific PCA geometries; fixed Qwen role-family table; released role/trait vectors. | Repeated nested model comparison, complete LOPO, role-family holdout, permutation null, OOD diagnostics, transparent Ridge bundles, endpoint-held-out synthetic interpolation; Qwen prediction CLI. | established cross-model same-space held-out reconstruction; behavioral realization and PC-semantic identity untested |
| Human-dataset feasibility, SAPA bridge review, and occupational-centroid stability | Determine whether independent human datasets contain adequate trait content and occupation structure for a later correspondence study without running that study. | Official SAPA V5 item/scale release; official NLSY97 public-use extraction and codebook; canonical trait definitions; prior conservative role/occupation mapping; frozen AA-1 and AA-5 specifications. | SAPA bridge with 45 direct links contracted to 12 moderate-or-better human structural proxies; NLSY97 stability tiers, error curves, corrected ICCs, and future candidate cells. | future-work feasibility only; neither human study supplies model-geometry evidence or a human/model correspondence test |
| Human-only SAPA bridge psychometric audit | Test whether the frozen direct/close SAPA proxies are coherent and discriminable in human responses before any human/model analysis. | Official SAPA V5 item responses and scoring keys; frozen Phase-1b bridge; psychometric rubric committed before covariance inspection. | Pairwise human proxy correlations/Ns, internal coherence, source convergence, reuse/discriminant audit, Big Five associations, effective dimensionality, and planned-missingness options. | future-work measurement diagnostic only; 12/45 direct links reach moderate-or-better support, but this is not model-geometry evidence or psychometric equivalence |
| Qwen-first human-construct bridge and correlation-defined family inventory | Preserve the separate Claude semantic review, build a sourced SAPA construct library, and inventory human measurements for mechanically selected positive/negative Qwen PC1-PC6 trait families. | Exact Claude review; frozen Codex review; primary SAPA/IPIP/SPI metadata; full 126-construct library; all 1,440 Qwen trait-PC associations; fixed 2,000-bootstrap family rule. | Review agreement and item-quality audit; 12 signed family summaries; neutral-ID mapping packet; 48-row inventory spanning 37 construct/item candidates and 350 SAPA items. | discovery/future-work measurement inventory only; no respondent scoring, cross-model validation, equivalence claim, or selected next experiment |
| Qwen axis-specific markers and purity-filtered SAPA inventory | Distinguish strong PC association from specificity within the supported Qwen PC1-PC6 subspace, then inspect available human measurement for the filtered families. | Saved 1,440 Qwen trait-PC associations; original 328 family memberships; 2,000 fixed-seed role bootstraps; unchanged 126-construct SAPA library; documented editorial composite config. | 88 primary markers; 328-row cross-loading classification; strength-purity/Pareto diagnostics; Affiliation composite specificity; 31-row filtered human inventory with 22 unique construct/item candidates and 195 items. | descriptive future-work inventory only; no respondent scoring/projection, human/model test, cross-model input, or next-experiment selection |
| AA-7 frozen-trait convergence and aligned role-score subspaces | Test a human-evidence-selected label set without human respondent projection, then compare activation-derived trait directions after held-out PC1-PC6 alignment. | Frozen AA-1 12 labels; AA-2 strict Big Five role scores; AA-3 model-local PC1-PC6 role scores; AA-4 nested compact and generic controls; saved 275 x 240 role-trait cosine matrices. | Matched held-out Ridge comparisons, 500-bank random/generic nulls, role-held-out Procrustes validation, 1,000-permutation nulls, aligned human-supported/Big Five directions, Agreeableness focal test. | primary compact convergence weak/absent; separate aligned model-direction recurrence strong; no human/model equivalence |
| Semantic prediction benchmark | Test how much text-derived semantic structure predicts canonical activation PCA3D. | Shared 273-persona benchmark rows; no-label/prompt-derived feature matrices. | Semantic baseline R2=0.389397. | established baseline |
| Codex trait replication | Test compact trait-like feature prediction outside the Claude Big Five source. | `research/q2_stability/qwen/outputs/codex_trait_replication/`. | Mean R2=0.398237. | weak positive signal |
| Codex procedural features | Test procedural/operating-mode features against canonical activation PCA3D. | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`. | Mean R2=0.490090. | supported but weaker than Big Five |
| Big Five benchmark | Test Big Five-style feature prediction. | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`; provenance audited in `research/outputs/big_five_provenance_audit/`. | Mean R2=0.612979. | strong compact predictor; partial activation-dependence caveat |
| Hierarchical trait-procedural model | Test whether procedural residual correction improves over trait-stage prediction. | `research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/`. | Hierarchical mean R2=0.622. | supported layered model evidence |
| Residual manifold analysis | Test targeted developmental/liminal/collective residual features after hierarchy. | `research/q2_stability/qwen/outputs/residual_manifold_analysis/`. | Mean R2=0.632. | tentative diagnostic layer |
| SVD15 residual model | Test lexical/register residual structure captured by TF-IDF SVD. | `research/q2_stability/qwen/outputs/residual_svd_interpretation/`; related Claude SVD15 result. | Mean R2=0.707. | strongest predictive result; lexical/register-sensitive |
| Coordinate-blind axis rubric validation | Test simple no-label prompt-text proxy rubrics for PC1/PC2/PC3. | `research/q2_stability/qwen/outputs/blinded_axis_rubric_validation/`. | Target correlations PC1 r=0.247, PC2 r=0.224, PC3 r=0.349; weak pairwise validation. | conservative/weak screen |
| Reading-based blinded rater study | Test whether GPT-5.5 reading of anonymized no-label dossiers recovers PC axes. | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`. | PC1 r=0.558, PC2 r=0.373, PC3 r=0.690; expanded CV R2 PC1=0.616, PC2=0.564, PC3=0.686. | supportive prompt-dossier evidence |
| Professional hierarchy validation | Test PC interpretations inside professional/persona subset. | `research/q2_stability/qwen/outputs/professional_hierarchy_validation/`. | PC1 objective certainty r=0.394; PC2 coherent uncertainty r=-0.007; PC3 system perturbation r=0.319. | PC1/PC3 modest support; PC2 weakened |
| PC1 competing-theories vocabulary test | Compare orderliness, determination, and external-standard-accountability vocabularies. | `research/outputs/pc1_competing_theories_test/`. | External-standard accountability best sparse vocabulary; incremental R2 over controls +0.0071. | supportive but weak |
| Blind PC interpretation rating benchmark | Test direct coordinate-blind GPT-5.5 ratings over role instructions. | `research/outputs/blind_pc_interpretation_rating_benchmark/`; five role instructions per persona. | PC1 R2=0.704; PC2 R2=0.423; PC3 R2=0.393; joint mean R2=0.525. | active support for compact PC interpretations |
| PC1 accountability intervention experiment | Test whether accountability/scrutiny wording moves PC1 beyond determination or arithmetic/checking. | `research/outputs/pc1_accountability_validation/`. | Accountability vs determination: +3.297 PC1, 5/5 pairs pass; accountability vs arithmetic/checking: +9.551 PC1, 5/5 pairs pass. | strong focused no-label intervention evidence |
| No-label elicitation Run 1 | Test frozen 60-prompt no-label packet relative to assistant role centroid. | `research/outputs/no_label_elicitation_validation/`. | 600/600 responses; 4/6 families pass. | partial activation-space support |
| Assistant centroid provenance audit | Determine whether assistant centroid is bare Qwen or released assistant role vector. | `research/outputs/assistant_centroid_provenance_audit/`. | Assistant centroid PC1=33.703, PC2=3.442, PC3=-5.156; not bare Qwen. | established methodological caveat |
| No-label geometry diagnostics | Place Run 1 family means, assistant centroid, and role centroids in shared PC space. | `research/outputs/no_label_elicitation_geometry_diagnostics/`. | Assistant PC1 percentile 83.3; PC1+ family moved negative PC1; `pc3_pos_05` mis-specified. | diagnostic evidence |
| Bare-Qwen baseline | Establish default extraction-question response centroid. | `research/outputs/no_label_elicitation_run2/`. | Bare-Qwen centroid PC1=23.510, PC2=14.041, PC3=-2.460. | foundational for future no-label interpretation |
| No-label elicitation Run 2 | Test revised PC1/PC2 prompts and minimal pairs relative to bare Qwen and assistant centroid. | `research/outputs/no_label_elicitation_run2/`. | 1,690/1,690 responses; PC1+ replacement 7/10 vs bare Qwen; PC2- replacement 9/10; PC2 minimal pairs 5/5; PC1 minimal pairs 1/5; PC3 cost-to-others 3/4 complete pairs. | active activation-space evidence |


### Methods Design Details Added for Drafting

These entries preserve Observed / Inferred distinctions and are intended to supply methods-section procedure details without drafting paper prose.

#### PC2 Conditional Validation

Source artifact: `research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md`; supporting table: `pc2_candidate_comparison.csv`; source ratings: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/axis_rater_scores.csv`.

Design details:

- Observed: 273 personas were common between `canonical_activation_pca3d.csv` and the blinded rater score table.
- Observed: PC1 conditioning used 10 equal-count PC1 percentile bands, roughly 27-28 personas per band, rather than fixed-width PC1 intervals. The report states this was chosen because the persona distribution is uneven and deciles preserve within-band sample size.
- Observed: the requested features tested were `abstraction`, `coherent_action_under_unresolved_uncertainty`, and `uncertainty_exposure`; the full candidate set also included `maturity`, `expertise` / `intelligence_expertise_score`, and `residence_time_under_uncertainty`.
- Observed: feature operationalization was rating-based, using Codex/GPT-5.5 blinded no-label prompt-dossier ratings from the prior rater study, not vocabulary counts or rule labels.
- Observed: `abstraction` was defined in the candidate table as conceptual, symbolic, theoretical, systemic, non-immediate representation; `coherent_action_under_unresolved_uncertainty` as capacity to keep making coherent progress without final resolution; `uncertainty_exposure` as how much uncertainty the role encounters independent of competence.
- Observed: procedure pooled within-band residual structure by demeaning PC2 and candidate scores within each PC1 decile band, then computing pooled band-demeaned Pearson correlation, pooled Spearman correlation, mean absolute within-band Pearson, and pooled R2.
- Observed: matched-pair analysis selected 75 pairs with `|PC1 difference| <= 5.0` and maximal PC2 separation, then compared candidate-score differences across high-PC2 versus low-PC2 members.
- Inferred: this is an approximate PC1 control, not a causal adjustment; it tests whether PC2-related ratings retain signal within local PC1 neighborhoods.

#### Blinded Axis Rater Study

Source artifact: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md`; runner: `research/q2_stability/qwen/scripts/blinded_axis_rater_study.py`; manifest: `rater_study_manifest.json`.

Design details:

- Observed: the rater saw anonymized persona dossiers with dossier IDs and five rewritten no-label prompts per persona from `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`.
- Observed: the rater did not see persona names, PCA coordinates, cluster labels, Big Five scores, residuals, or prior interpretation labels. The report states no full 275-persona rollout-response corpus was found locally, so no generated response text was used for all personas.
- Observed: coverage was 275 personas, 5 records per persona, split into 14 rater-prompt chunks.
- Observed: scoring was Codex/GPT-5.5 as reading-based rater, one prepared annotation pass over prompt chunks, with JSON outputs later analyzed. This is Codex-as-rater, not independent human annotation or a second-model panel.
- Observed: all ratings used 0-100 scales.
- Observed: PC1 rubric was `pc1_objective_certainty_score`: high means the role objective is rule-bound, externally specified, compliance/checking/validation oriented; low means the objective must be interpreted, negotiated, discovered, or constructed under ambiguity.
- Observed: PC2 rubric was `pc2_coherent_action_under_uncertainty_score`: high means coherent action collapses or fragments under uncertainty, including impulsive, avoidant, developmentally unstable, or unable to integrate ambiguity; low means the role can sustain coherent action under unresolved uncertainty. The prompt explicitly says to score competence/capacity under unresolved uncertainty, not amount of uncertainty.
- Observed: PC3 rubric was `pc3_antagonistic_transgressive_score`: high means antagonistic, adversarial, disruptive, transgressive, norm-inverting, conflict-generating; low means cooperative, nurturing, stabilizing, mediating, caring, reconciling.
- Observed: PC2 alternatives were also rated: maturity, abstraction, intelligence/expertise, uncertainty exposure, and uncertainty residence time.
- Observed: analysis computed Pearson and Spearman correlations between each score and PC1/PC2/PC3, linear regression train R2 and 5-fold CV R2 with seed 42, 500-permutation nulls, and 20 close-orthogonal matched pairs per target PC.

#### Professional Hierarchy Validation

Source artifact: `research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md`; runner: `research/q2_stability/qwen/scripts/professional_hierarchy_validation.py`; manifest: `professional_inventory_manifest.json`.

Design details:

- Observed: the professional subset was selected from a predefined list of broad expert, applied, academic, institutional, analytic, and professional-function personas embedded in the runner. Roles were retained only if present in both the Qwen geometry corpus and the no-label prompt corpus.
- Observed: the resulting professional inventory contained 102 personas. Requested examples absent from the corpus included `systems engineer`, `professor`, `investigative journalist`, and `reformer`.
- Observed: the rater saw dossier IDs and five rewritten no-label prompts per professional persona; persona names, coordinates, clusters, prior interpretations, Big Five scores, residuals, and prior labels were removed during rating.
- Observed: scoring used Codex/GPT-5.5 as a reading-based rater over the no-label prompt dossiers, not a deterministic lexical proxy.
- Observed: the three rated features were `objective_certainty_score`, `coherent_uncertainty_capacity_score`, and `system_perturbation_score`, all on 0-100 scales with short text-grounded rationales.
- Observed: objective certainty asked whether success is determined by externally specified criteria rather than internally negotiated goals; high examples included compliance, checking, validation, auditing, proofreading, and accounting.
- Observed: coherent uncertainty capacity asked how effectively the role can keep making coherent progress while the correct answer, objective, or resolution remains unavailable; the prompt explicitly says not to score amount of uncertainty or complexity.
- Observed: system perturbation asked whether the role primarily maintains/repairs/stabilizes/coordinates an existing structure or challenges/stress-tests/perturbs/disrupts it.
- Observed: analysis computed Pearson and Spearman correlations for each score against PC1/PC2/PC3, target-direction support flags, predicted and actual rankings, and 5-fold CV R2 from the three standardized professional ratings using seed 42 and ordinary least-squares/pseudoinverse regression.

#### PC1 Competing-Theories Vocabulary Test

Source artifact: `research/outputs/pc1_competing_theories_test/pc1_competing_theories_report.md`; runner: `research/outputs/pc1_competing_theories_test/run_pc1_competing_theories_test.py`.

Design details:

- Observed: the analysis used the five positive role-conditioning instructions per role from `data/roles/instructions/*.json` for the 273 common personas in the shared benchmark.
- Observed: vocabulary family `A_orderliness_conscientiousness` used exact terms: `tidy`, `orderly`, `neat`, `organized`, `symmetry`, `punctual`, `disciplined`, `careful`, `structured`.
- Observed: vocabulary family `B_determination_explicit_criteria` used exact terms: `determine`, `qualify`, `pass`, `fail`, `eligibility`, `approval`, `certification`, `admissibility`, `compliance decision`.
- Observed: vocabulary family `C_external_standard_accountability` used exact terms: `evidence`, `methodology`, `verification`, `scrutiny`, `validation`, `audit`, `protocol`, `standards`, `requirements`, `peer review`, `regulatory review`, `independent criteria`, `accountability`.
- Observed: terms were counted case-insensitively on lowercased text using regex word/phrase boundary matching. No stemming, lemmatization, semantic expansion, or fuzzy matching was used.
- Observed: both raw counts and length-normalized counts per 1,000 tokens were computed; signed contrasts `C-A`, `C-B`, and `B-A` were also computed.
- Observed: controls included log text length and Qwen cluster one-hot controls from `research/geometry_tables/qwen_role_pc_rankings.csv`.
- Observed: procedures included Pearson and Spearman correlations with PC1, partial correlation controlling text length, cluster-and-length controlled correlation by residualizing both feature and PC1, and held-out Ridge regression with `alpha=1.0` under the same deterministic split assignments as the shared latent-feature benchmark.
- Observed: the report states control-only held-out regression using text length plus cluster already reached PC1 R2=0.774, so incremental R2 over those controls is the stricter comparison.

#### PC3 Perturbation-Stabilization Validation

Source artifact: `research/outputs/pc3_validation/pc3_validation_report.md`.

Design details:

- Observed: the data source was `research/visualizations/geometry_viz_data.json`, using `roles.pca3d` with PC3 at index 2.
- Observed: 275 personas were scored.
- Observed: scoring used persona name plus extracted neutral role definition from `data/roles/instructions`; PC coordinates and clusters were joined only after scoring.
- Observed: operationalization was deterministic rubric scoring, not independent human or LLM judgment. The report does not identify it as vocabulary-based; it is a rule/rubric-based manual/deterministic scoring procedure over names plus definitions.
- Observed: the exact 1-7 perturbation-stabilization rubric was: 1 = strongly stabilizing, nurturing, healing, mediating, preserving, protecting, supporting, or restoring systems; 2 = mostly stabilizing, with limited challenge or intervention; 3 = mildly stabilizing or support-oriented; 4 = neutral, mixed, or unclear; 5 = mildly perturbative, probes, challenges, tests, audits, diagnoses, disputes, or intervenes without clear destructive intent; 6 = strongly perturbative/interventionist, penetrates, stress-tests, exploits weaknesses, disrupts, investigates, debugs, argues, or forces change; 7 = extremely perturbative, chaotic, corrupting, predatory, destructive, sabotaging, or intentionally destabilizing.
- Observed: analysis computed global Pearson and Spearman correlations with PC3, within-cluster pairwise ordering accuracy, within-cluster Pearson/Spearman for target clusters, cluster-dummy residualized partial Pearson/Spearman, leave-one-cluster-out rank/order prediction, and negative-control comparisons against moral badness, professionalism, weirdness/fantasticality, and abstraction.

#### PC1 Accountability Intervention Experiment

Source artifact: `research/outputs/pc1_accountability_validation/accountability_validation_report.md`; prompt catalog: `prompt_catalog.csv`; runner: `run_pc1_accountability_validation.py`.

Design details:

- Observed: two experiments used five matched pairs each, 10 samples per version, for 20 prompt versions and 200 total Qwen/Qwen3-32B generations.
- Observed: extraction protocol matched Run 2: one fresh user message per sample, no system prompt or prior history, direct forward hook on `model.model.layers[48]`, mean pooling over generated assistant response tokens only, separate no-cache forward extraction pass, and same reconstructed Qwen persona PCA basis/sign alignment as Run 2.
- Observed: Qwen saw prompt text only; prompt IDs, experiment labels, pair labels, PC labels, hypotheses, and metadata were not visible.
- Observed: Experiment A compared determination framing to accountability/scrutiny framing. Verbatim pairs:
  - A1 determination: "A financial report submitted to an external regulator states total expenses of $9,860. The attached supporting records contain line items of $1,200, $3,450, $2,010, and $3,400. Regulatory guidance requires reported totals to match supporting documentation exactly. Determine whether the report is correct."
  - A1 accountability/scrutiny: "A financial report submitted to an external regulator states total expenses of $9,860. The attached supporting records contain line items of $1,200, $3,450, $2,010, and $3,400. Regulatory guidance requires reported totals to match supporting documentation exactly. Should the report be accepted for filing? State your finding and explain the basis for it."
  - A2 determination: "A laboratory seeks accreditation. Accreditation standards require calibration records demonstrating compliance with a 30-day calibration interval. The last calibration occurred on April 1 and the next on May 6. Determine whether the record satisfies the requirement."
  - A2 accountability/scrutiny: "A laboratory seeks accreditation. Accreditation standards require calibration records demonstrating compliance with a 30-day calibration interval. The last calibration occurred on April 1 and the next on May 6. Would this record satisfy the accreditation requirement? State the finding and identify the specific basis for acceptance or rejection."
  - A3 determination: "A compliance certification submitted to headquarters states that a department satisfied all mandatory training requirements. Records show 47 of 50 employees completed the course, while policy requires 100% completion by quarter end. Determine whether the statement is accurate."
  - A3 accountability/scrutiny: "A compliance certification submitted to headquarters states that a department satisfied all mandatory training requirements. Records show 47 of 50 employees completed the course, while policy requires 100% completion by quarter end. Can the certification be signed? State your determination and the evidence supporting it."
  - A4 determination: "An organization is responding to a privacy audit. A file states that customer consent was obtained before data sharing, but no consent record is attached. Determine whether the file is complete."
  - A4 accountability/scrutiny: "An organization is responding to a privacy audit. A file states that customer consent was obtained before data sharing, but no consent record is attached. Audit standards require documentary evidence supporting every consent claim. Can the file withstand audit review? State your finding and identify the missing evidence."
  - A5 determination: "During an internal controls review, a vendor invoice requests payment for 42 units while the approved purchase order authorizes only 40. Company policy requires documented approval before any overage may be paid. Determine whether payment should be authorized."
  - A5 accountability/scrutiny: "During an internal controls review, a vendor invoice requests payment for 42 units while the approved purchase order authorizes only 40. Company policy requires documented approval before any overage may be paid. Should the payment be authorized? Issue a finding and cite the controlling requirement."
- Observed: Experiment B compared arithmetic/checking framing to accountability/scrutiny framing. Verbatim pairs:
  - B1 arithmetic/checking: "A spreadsheet total says $9,860, but the listed line items are $1,200, $3,450, $2,010, and $3,400. Is the total accurate?"
  - B1 accountability/scrutiny: same as A1 accountability/scrutiny above.
  - B2 arithmetic/checking: "A checklist says equipment calibration must occur every 30 days. The last calibration was April 1 and the next was May 6. Did the process meet the standard?"
  - B2 accountability/scrutiny: same as A2 accountability/scrutiny above.
  - B3 arithmetic/checking: "A department claims it met the quarterly training requirement because 47 of 50 employees completed the course. The standard requires 100% completion by quarter end. Is the claim compliant?"
  - B3 accountability/scrutiny: same as A3 accountability/scrutiny above.
  - B4 arithmetic/checking: "A form asks whether customer consent was obtained before data sharing. The box is checked yes, but no consent record is attached. Is the file complete?"
  - B4 accountability/scrutiny: same as A4 accountability/scrutiny above.
  - B5 arithmetic/checking: "A vendor invoice lists 42 units at $18 each, but the purchase order approved 40 units at $18 each. The policy says overages require written approval before payment. Should this invoice be approved as-is?"
  - B5 accountability/scrutiny: same as A5 accountability/scrutiny above.
- Observed: analysis computed prompt means, pairwise B-A PC1/PC2/PC3 effects, bootstrap 95% CIs, pass/fail by pair, deltas versus the Run 2 bare-Qwen baseline, and deltas versus the released assistant-role centroid.

#### PC2 Muted-PC1 Extremes Analysis

Source artifact: `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_extremes_report.md`.

Design details:

- Observed: geometry source was `research/visualizations/geometry_viz_data.json`.
- Observed: the selected muted-PC1 band was the central 10% band, PC1 45th to 55th percentile, because it yielded enough roles for stable inspection.
- Observed: numeric PC1 bounds were -2.747954 to 6.917357 and included 27 roles/personas.
- Observed: fallback bands were computed but not used: central 20% / 40-60 percentile yielded 55 roles, and central 30% / 35-65 percentile yielded 83 roles.
- Observed: within the selected band, roles were ranked by PC2 descending and ascending. The analysis reported top 10 high-PC2 roles, bottom 10 low-PC2 roles, full ranking, PC1/PC2/PC3 coordinates, percentiles, cluster labels, and plots.
- Observed: caution note in the report states the selected band is cluster-skewed, with procedural_professional accounting for 13/27 roles.

#### Blind PC Interpretation Rating Benchmark

Source artifacts: `research/outputs/blind_pc_interpretation_rating_benchmark/blind_pc_interpretation_rating_report.md`, `run_blind_pc_interpretation_rating_benchmark.py`, `blind_rating_results.json`, `role_dimension_ratings.csv`, and `benchmark_comparison.csv`.

Design details:

- Observed: rater model was `gpt-5.5` through Codex CLI; `model_used` is GPT-5.5.
- Observed: benchmark sample size was 273 personas, matching the canonical shared Qwen activation PCA3D benchmark rows.
- Observed: the rater saw only the five role instructions for each role from `data/roles/instructions/*.json`.
- Observed: the rater did not see PC coordinates, PCA labels, rankings, cluster assignments, assistant-axis values, geometry information, or benchmark targets. The role instructions themselves contain role wording; the blinding is to geometry, not to role text.
- Observed: ratings were generated in batches through Codex CLI using `-m gpt-5.5`, read-only sandboxing, a temporary non-repo working directory, strict JSON output, and no file/tool inspection by the rater.
- Observed: Dimension 1, External-Standard Accountability, used a 1-10 rubric where 1 means outputs answer primarily to internal vision, instinct, expression, preference, or discretion, and 10 means outputs must withstand scrutiny against standards independent of the speaker, such as evidence, methodology, requirements, protocol, law, regulations, peer review, or established criteria.
- Observed: Dimension 2, Integration / Coherence of Wholes, used a 1-10 rubric where 1 means immediate situations, local experience, practical encounters, direct engagement with particulars, and 10 means underlying structure, systems, persistent patterns, identity through change, coherence of larger wholes. For PC2 prediction, the signed value `-integration_coherence_wholes_raw` was used because higher integration maps to more negative PC2.
- Observed: Dimension 3, Internal Objective vs Care Orientation, used a 1-10 rubric where 1 means organized around care, obligation, protection, service, responsibility toward others, and 10 means organized around an internal objective, agenda, drive, or goal independent of others' outcomes.
- Observed: evaluation used the same five deterministic split assignments from `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_split_assignments.csv` as the shared benchmark.
- Observed: model family A used only `external_standard_accountability` to predict PC1; model family B used only signed integration to predict PC2; model family C used only `internal_objective_vs_care` to predict PC3; model family D used all three ratings jointly to predict all three PCs.
- Observed: each fold standardized features with `StandardScaler`, fit Ridge regression with `alpha=1.0` on train roles, computed held-out R2 on held-out roles, and averaged R2 across the five canonical splits. The comparison table included semantic baseline, Codex trait replication, Codex procedural features, Claude Big Five, hierarchical model, residual manifold, and semantic+BigFive+SVD15 prior benchmark families.

#### Trait-Profile PC Predictor Generalization

Source artifact: `research/outputs/trait_profile_pc_predictor/trait_profile_pc_predictor_report.md`; machine-readable summary: `validation_summary.json`; complete held-out tables: `nested_cv_oof_predictions.csv`, `leave_one_persona_out_predictions.csv`, and `leave_one_cluster_out_predictions.csv`.

Design details:

- Observed: the input matrix contains 275 unique personas x 240 unique finite activation-space cosine features and aligns exactly, in order, with canonical `geometry_viz_data.json` role names and the canonical cluster table. The matrix reproduces from mean-pooled/L2-normalized released Qwen role/trait vectors to max absolute error 5.55e-16.
- Observed: model comparison used 5 shuffled outer folds repeated across 10 deterministic seeds and 4-fold inner tuning. Ridge, PLSRegression, RBF Kernel Ridge, and distance-weighted KNN were evaluated on raw cosines and training-fold-only quantile transforms. Quantile fitting, feature scaling, component/neighbor/kernel/alpha selection, and target fitting were all confined to training partitions.
- Observed: complete Ridge LOPO removed each of 275 personas before alpha selection and fitting. Raw-cosine LOPO R2 was PC1=0.999522, PC2=0.998811, PC3=0.999611; normalized 3D RMSE=0.045378. Fold-safe quantile LOPO R2 was 0.997556/0.988048/0.989209; normalized 3D RMSE=0.159028.
- Observed: Ridge was the best raw-profile model in repeated nested CV (R2=0.999465/0.998718/0.999567; normalized 3D RMSE=0.047591). PLS, Kernel Ridge, and KNN did not clear the predeclared 10% normalized-RMSE improvement rule, so transparent Ridge remains V1.
- Observed: leave-one-canonical-cluster-out Ridge aggregate R2 was 0.998692/0.997740/0.999338; normalized 3D RMSE rose to 0.067997 and mean normalized error to 1.68x LOPO. Editorial had the largest per-cluster normalized RMSE (0.1062); mythic/spiritual and procedural/professional each had about 2x their cluster-specific LOPO mean error.
- Observed: the 100-permutation nested Ridge control stayed below chance (mean per-PC R2=-0.024420; p95=-0.007548). LOPO error was modestly associated with fold-local 5-NN distance and PCA reconstruction residual, supporting their use as descriptive context but not calibrated uncertainty.
- Observed: the canonical PCA basis reproduced from all 275 mean-pooled role vectors at max error 1.207e-06. Across 120 synthetic convex activation-vector mixes from 40 near/distant pairs, with both pair endpoints omitted from each fit, R2 was 0.995266/0.984377/0.997144; distant-pair mixes were harder.
- Interpretation boundary: this is same-space Qwen activation-derived reconstruction and interpolation. Counterfactual percentile edits are predicted locations under the learned map, not observed behavior or causal trait interventions. Generalization to a genuinely new elicited persona, other models, frontier systems, or humans remains untested.

#### Llama/Gemma Trait-Profile Predictor Replication

Source artifact: `research/outputs/multimodel_trait_profile_pc_predictor/multimodel_trait_profile_pc_predictor_report.md`; comparison table: `cross_model_comparison.csv`; machine-readable model summaries: `llama/validation_summary.json` and `gemma/validation_summary.json`.

- Observed: both released/local bundles contain exactly the same intended 275 persona labels and 240 trait labels, with finite bfloat16 source tensors. The exact established within-model PCA reconstruction/orientation procedure reproduces saved Llama coordinates to max error 2.748e-14 and Gemma to 1.376e-11.
- Observed: raw Ridge LOPO R2 is 0.997833/0.997161/0.989900 for Llama (normalized 3D RMSE 0.124494) and 0.999788/0.996179/0.987835 for Gemma (0.127824), compared with canonical Qwen 0.999522/0.998811/0.999611 (0.045378).
- Observed: fold-safe quantile Ridge remains strongly predictive but less precise in both replications, with normalized RMSE 0.328303 for Llama and 0.304909 for Gemma. Quantile Kernel Ridge improves over quantile Ridge in repeated nested CV, but raw Ridge remains the best overall representation/model and the selected transparent family.
- Observed: applying the fixed Qwen-canonical role-family partition cross-model yields aggregate Ridge R2 0.993894/0.993627/0.977094 and normalized RMSE 0.204224 for Llama; Gemma yields 0.999271/0.993851/0.975087 and 0.176110. Mean normalized error is 1.810x and 1.535x LOPO. These labels are not model-native clusters.
- Observed: 100-permutation p95 mean-PC R2 is -0.009359 for Llama and -0.011572 for Gemma, with no leakage anomaly. Training-only OOD/error association is stronger in Llama (5-NN Pearson 0.650; reconstruction residual 0.614) than Gemma (0.383/0.379) or Qwen (0.243/0.300), but remains descriptive rather than calibrated uncertainty.
- Observed: 120 endpoint-held-out synthetic mixtures reach R2 0.983420/0.982280/0.946688 for Llama and 0.999557/0.980280/0.969824 for Gemma. Nearby/distant normalized RMSE is 0.0650/0.4638 and 0.0669/0.2964; pair-level endpoint distance correlates with error at Pearson r=0.870/0.774.
- Observed: a full second fixed-seed run reproduced all 20 deterministic model CSVs byte-for-byte. Ridge remains selected for Qwen, Llama, and Gemma under the predeclared 10% normalized-RMSE improvement/no-harder-holdout-degradation rule.
- Interpretation boundary: replication supports approximately linear same-space trait-bank coverage across three saved open-model vector sets. It does not establish identical PC semantics across models, independent psychological validity, causal trait determination, behavioral realization, transfer to humans, or relative psychological sophistication/human-likeness.

#### Extended Persona PCA Dimensionality Audit

Source artifact: `research/outputs/extended_persona_pca/extended_persona_pca_report.md`; construction audit: `persona_pca_construction_audit.md`; full spectrum: `full_pca_spectrum.csv`; retention table: `component_retention_summary.csv`.

- Observed: the original geometry script explicitly requested three components for a 3D visualization. It did not run a scree, cumulative-variance, parallel-analysis, or bootstrap cutoff. The audited PCA inputs are 275 mean-pooled saved role vectors by 5,120 Qwen, 8,192 Llama, or 4,608 Gemma activation coordinates. The 240 named traits do not enter PCA.
- Observed: Qwen PC1-PC10 explain 31.595%, 16.163%, 8.690%, 4.520%, 3.615%, 2.824%, 2.536%, 2.138%, 1.946%, and 1.601%, reaching 75.630% cumulatively. The smallest Qwen k is 7 for 68% and 15 for 80%; corresponding 68% counts are 17 Llama and 14 Gemma.
- Observed: Qwen's largest absolute and relative eigengap is after PC1, while both deterministic log-scree methods place the Qwen knee/break at PC11. Sequential 95th-percentile marginal-preserving parallel analysis retains 13 Qwen, 35 Llama, and 25 Gemma components. The methods disagree, so no one cutoff is treated as ground truth.
- Observed: under 500 role bootstraps with one-to-one absolute-loading-cosine Hungarian matching and sign correction, only Qwen PC1-PC3 meet the strict individual-axis rule. No later adjacent Qwen pair passes the strict subspace rule. PC4-PC6 meet a declared moderate reproducibility rule; PC8/PC10 do as well but have weaker trait coherence.
- Observed: Qwen PC4, PC5, and PC6 each exceed the sequential null, have a same-space trait association |r|>=0.50, and recur in both models after a 1,000-shuffle search-adjusted role-label control. Best absolute Pearson matches are PC4 to Llama PC3/Gemma PC4 at 0.690/0.628, PC5 to PC5/PC5 at 0.688/0.651, and PC6 to PC6/Gemma PC8 at 0.505/0.570. Top-4/top-5/top-6 mean score-subspace canonical correlations are 0.908/0.891/0.888 for Qwen-Llama and 0.877/0.911/0.817 for Qwen-Gemma (all empirical p=0.001).
- Interpretation: retain PC1-PC3 as the compact/named scientific core. PC1-PC6 may be used when weaker supported secondary coordinates are relevant, but PC4-PC6 should remain explicitly secondary and provisionally interpreted. PC8/PC10 are exploratory; other tested later axes are not privileged even when they exceed the random-data null.
- Interpretation boundary: score recurrence over shared role labels may partly reflect shared role-instruction structure and does not establish identical cross-model PC semantics. Explained variance is centered saved-role activation-coordinate variance, not percent personality, behavior, human psychological variation, or causal importance. Trait associations remain same-space evidence.
- Verification: all 274 components reconstruct each model's centered role matrix; canonical PC1-PC3 reproduce to max error 1.207e-06/2.748e-14/1.376e-11 for Qwen/Llama/Gemma; 14 major numerical outputs are byte-identical on a complete second pass; independent verification passes 17/17 checks.

#### Qwen Trait Sparsity and Basis-Coverage Audit

Source artifact: `research/outputs/qwen_trait_sparsity_prediction/qwen_trait_sparsity_report.md`; machine-readable summary: `validation_summary.json`; matched controls: `matched_basis_comparison.csv`; direct span audit: `trait_span_pc_coverage.csv`.

- Observed: canonical persona PCA fits the 275 x 5,120 mean-pooled role-activation matrix without trait inputs. Predictor features and PC targets nevertheless transform the same role vectors, producing same-space algebraic dependence without direct target-column leakage.
- Observed: the exact full-bank baseline reproduces at R²=0.999522/0.998811/0.999611 and normalized RMSE=0.045378. Leakage-safe joint selection reaches all-PC R²>=.95/.98/.99 at k=3/4/6 and normalized RMSE<=.10/<=2x-full at k=12/14.
- Observed: selected 5/10/15 real traits reach normalized RMSE=0.176511/0.106880/0.087216. At k=15 optimized real traits beat all 100 random-real, isotropic, and fold-local persona-span banks, demonstrating a compact semantic-efficiency advantage.
- Observed: generic coverage becomes decisive at high k. At k=240, fold-local training-persona-span directions reach 0.051422 versus 0.047609 for the full real-trait bank; the real-trait span contains 98.7955%/98.5303%/98.1947% of Qwen PC1/PC2/PC3 loading directions.
- Interpretation boundary: the result is a mixture of compact real-trait alignment and high-dimensional generic same-space reconstruction. It does not establish an independently validated psychological ontology, causal traits, human correspondence, or behavioral realization.

#### Externally Anchored Big Five Audit

Source artifact: `research/outputs/externally_anchored_big_five/externally_anchored_big_five_report.md`; focal result: `agreeableness_pc3_focal_test.json`; frozen mappings: `human_anchored_strict_trait_mapping.csv`, `human_anchored_extended_trait_mapping.csv`, and `external_taxonomy_expanded_trait_mapping.csv`.

- Observed: mapping A/B/C was frozen before geometry analysis at commit `636c5c1d9b832a1199e8d5b35dea993a41f94d4b`; no persona coordinates, PC correlations, AA-4 results, clusters, surfaces, or motivating screenshot were available to the mapping generator.
- Observed: strict uses 42 defensible domain assignments among reviewed `ACCEPT_DIRECT`; extended adds 25 separately flagged `ACCEPT_CLOSE`; external-expanded uses 109 high-confidence direct indicators after all 240 traits were reviewed; the historical composite remains comparator D.
- Observed: strict Qwen Agreeableness versus PC3 has direction cosine -0.847133, Pearson r=-0.881714, Spearman rho=-0.837526, R²=0.777420, joint standardized beta=-0.894047, and held-out partial R²=0.524122. Extended, expanded, and historical constructions remain strongly aligned.
- Observed: cross-model placement is not universal. Llama Agreeableness-PC3 is weak and Agreeableness instead aligns mainly with negative PC2; Gemma has a moderate PC3 relation plus a substantial PC1 association.
- Interpretation: negative Qwen PC3 has a strong Agreeableness-related component that sharpens but does not replace the broader care/repair/stabilization versus disruptive/internal-objective wording.
- Boundary: external anchoring improves construct transparency but remains same-space activation evidence, not independent human psychometric validation, model/human correspondence, behavioral realization, causal trait evidence, or identical cross-model PC semantics.

#### Qwen-First Human-Construct Source and Correlation-Defined SAPA Inventory

Source artifacts: `research/outputs/qwen_pc_human_construct_bridge/qwen_pc_human_construct_bridge_report.md` and `research/outputs/qwen_trait_family_human_inventory/qwen_pc_trait_family_human_inventory_report.md`; machine-readable inventory: `qwen_pc_trait_family_human_inventory.csv`.

- Observed: the separate Claude Opus 5 semantic review agrees exactly with the frozen Codex review on 69/78 rows (88.46%; unweighted kappa 0.785), with nine explicit discordances. Eight flagged item wording/direction cases were checked against primary SAPA/IPIP/SPI sources, and historical packets remain unchanged.
- Observed: a sourced human inventory contains 126 SAPA constructs across domain, aspect, facet, and narrow levels. The later family analysis saved all 1,440 Qwen PC1-PC6 x trait associations and selected membership mechanically at absolute Pearson r at least 0.50, PC-local BH-FDR q below 0.01, and at least 95% sign stability across 2,000 role bootstraps.
- Observed: 328 signed memberships span 238 unique traits. A neutral-ID packet was frozen before mapping to the full library. The resulting 48-row measurement inventory contains 37 unique construct/item candidates and 350 unique SAPA items; family-level best availability is 4 strong, 5 partial, 1 facet/item-only, and 2 empty-pole no-match cases.
- Interpretation: the inventory makes broad, facet, and item-level SAPA availability inspectable for numerical Qwen trait families without assuming a literal one-to-one trait bridge. Proposed semantic family matches remain interpretations, not empirical human/model correspondence.
- Boundary: this is future-work context, not Paper 1.5 model-geometry evidence. No respondent was scored or projected, no Llama/Gemma or AA-7 result determined the matching, and no next experiment was selected.

#### Axis-Specific Qwen Trait Markers and Purity-Filtered SAPA Inventory

Source artifact: `research/outputs/qwen_trait_axis_specificity/qwen_axis_specific_family_report.md`; primary markers: `qwen_axis_specific_marker_sets.csv`; human inventory: `qwen_axis_specific_human_inventory.csv`.

- Observed: a rule frozen before specificity results requires original strong-family membership, target-axis dominance, at least 95% bootstrap dominance across 2,000 role resamples, and at least 70% of six-PC communality on the target. It retains 88/328 signed memberships: PC1 12/48, PC2 3/10, PC3 7/8, and PC4-PC6 zero on both poles.
- Observed: 150 original memberships are target-dominant but diffuse and 90 are non-target-dominant. The existing editorial Affiliation mean is strongly PC3-specific (`r=-0.970129`, purity `0.965818`, dominance gap `0.842644`).
- Observed: neutral-ID remapping against the full unchanged library yields 22 unique construct/item candidates and 195 items; three signed families retain strong whole-family matches, three partial-only matches, and six empty primary-marker families no match.
- Interpretation: specificity narrows the available human counterpart set and isolates cleaner PC1-PC3 markers, but removed cross-loaders remain legitimate compound trait associations. This is not human/model correspondence evidence and is not part of the Paper 1.5 model-geometry claim chain.

#### AA-7 Human-Supported Trait Convergence and Aligned Subspaces

Source artifact: `research/outputs/human_supported_trait_convergence/human_supported_trait_convergence_report.md`; matched comparison: `comparator_summary.csv`; alignment evidence: `procrustes_alignment_cv.csv` and `procrustes_alignment_null.csv`; aligned directions: `aligned_human_supported_trait_directions.csv` and `aligned_big_five_directions.csv`.

- Observed: the exact 12 AA-1 moderate-or-better labels and support levels were frozen before geometry outcomes. The human-supported family beat 0/6 matched random-real k=12 nulls (core/extended p=0.2395/0.2615 Qwen, 0.7405/0.3533 Llama, and 0.1497/0.1257 Gemma) and 2/6 fold-local persona-span nulls (Qwen core p=0.0220; Gemma core p=0.0279); the preregistered primary classification is weak/absent. Geometry-optimized k=12 sets were better for every model/scope. The frozen set beat isotropic ambient controls in all six comparisons, but isotropic is the weaker generic control.
- Observed: role-held-out PC1-PC6 alignment mean coordinate correlations are 0.879 Llama→Qwen, 0.809 Gemma→Qwen, and 0.908 Gemma→Llama; each exceeds a 1,000-permutation role-label null at p=0.001. Eleven frozen directions recur highly and one moderately; all five strict Big Five directions recur highly.
- Observed: Agreeableness is reconciled after alignment, with pairwise cosines 0.900/0.952/0.938 and squared-cosine consensus fractions 0.948/0.939/0.973. Adding PC4-PC6 materially increases recurrence for the frozen 12, Big Five, and Agreeableness.
- Interpretation: AA-7 does not show that human psychometric defensibility identifies unusually efficient compact model coordinates. It does show cross-model recurrence of the corresponding model activation-derived directions after rotation, supporting a shared low-dimensional role-space organization broader than Big Five.
- Boundary: shared English role labels/instructions, possible training-data overlap, and possible common representational structure are unresolved sources of recurrence; no causal interpretation follows. No human respondent or occupational centroid was projected, no human microdata were committed, and the preregistered gate for designing a respondent-projection study failed.

## 3. Benchmark Progression

Chronological benchmark table:

| Order | Benchmark | Primary artifact | R2 / mean R2 | Status | Interpretation |
|---:|---|---|---:|---|---|
| 1 | Semantic baseline | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv` | 0.389397 | established baseline | Semantic topology partially predicts activation topology but does not explain it away. |
| 2 | Codex trait replication | `research/q2_stability/qwen/outputs/codex_trait_replication/codex_trait_replication_report.md` | 0.398237 | weak positive | Slightly above semantic baseline; not a successful replication of stronger Big Five result. |
| 3 | Codex procedural features | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv` | 0.490090 | supported | Procedural/behavioral features add useful signal beyond semantic baseline. |
| 4 | Big Five benchmark | `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv`; `research/outputs/big_five_provenance_audit/` | 0.612979 | observed strong compact predictor | Strong compact prediction; provenance partially activation-dependent and heuristic. |
| 5 | Hierarchical model | `research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/hierarchical_model_report.md` | 0.622 | supported | Procedural residual correction modestly improves over trait stage. |
| 6 | Residual manifold | `research/q2_stability/qwen/outputs/residual_manifold_analysis/residual_manifold_report.md` | 0.632 | tentative | Developmental/liminal/collective residual features add a small diagnostic layer. |
| 7 | SVD15 model | `research/q2_stability/qwen/outputs/residual_svd_interpretation/residual_svd_interpretation_report.md` | 0.707 | observed strong predictive result | Lexical/register SVD structure is strongest predictor; not yet distilled into stable human-readable factors. |

Related non-chronological comparison:

| Benchmark | Primary artifact | R2 / mean R2 | Status | Interpretation |
|---|---|---:|---|---|
| GPT-5.5 blind three-axis interpretation ratings | `research/outputs/blind_pc_interpretation_rating_benchmark/benchmark_comparison.csv` | 0.525022 | active/supportive | Compact PC interpretations predict geometry better than semantic baseline and Codex procedural features, but below Big Five/hierarchy/residual/SVD families. |
| Complete activation-derived trait profile | `research/outputs/trait_profile_pc_predictor/trait_profile_pc_predictor_report.md` | LOPO R2 0.999522/0.998811/0.999611 | established, provenance-coupled | Near-ceiling same-space basis reconstruction under persona and cluster holdouts; not comparable to compact independent/semantic feature benchmarks as psychological evidence. |
| Cross-model complete trait profiles | `research/outputs/multimodel_trait_profile_pc_predictor/cross_model_comparison.csv` | Llama LOPO R2 0.997833/0.997161/0.989900; Gemma 0.999788/0.996179/0.987835 | established replication, provenance-coupled | Same-space mapping replicates in model-specific PCA geometries; accuracy differences are not psychological comparisons and oriented axes need not share semantics. |
| Qwen compact traits and matched generic bases | `research/outputs/qwen_trait_sparsity_prediction/` | 3/4/6 traits reach all-PC R²>=.95/.98/.99; k=240 persona-span RMSE=0.0514 vs full real 0.0476 | established mixed same-space result | Compact optimized real traits are efficient, while high-k near-ceiling prediction is substantially generic basis coverage. |
| Frozen externally anchored Big Five | `research/outputs/externally_anchored_big_five/` | Qwen strict Agreeableness-PC3 cosine=-0.847; r=-0.882; R²=0.777; held-out partial R²=0.524 | strong same-space component evidence | Negative Qwen PC3 has a major Agreeableness-related component; Llama/Gemma reject a universal PC3 identity. |

## 4. Current PC1 Interpretation

Current wording:

- PC1: convergence pressure / external-standard accountability / disciplined evaluative competence versus degrees of freedom / open symbolic or expressive possibility.

Final wording for methods/writing handoff:

- Observed/Inferred wording: PC1 measures the degree to which a role's outputs must answer to a standard that exists independently of the speaker.
- Shorthand: rigor.
- Inferred clarification: high rigor means the standard is external, pre-existing, and indifferent to the speaker's preferences. Low rigor means the output answers to nothing outside the speaker: own vision, instinct, expression, or intrinsic nature.
- Interpretive note: this resolves the arithmetic anomaly because arithmetic is self-contained verification, not accountability to an external standard.
- Interpretive note: this resolves the robot-below-auditor gap because the robot executes procedure, but does not issue a finding that must withstand scrutiny.
- Status: these are interpretations supported by the current evidence, not direct observations or proven causal semantics.

### Observed Findings

| Finding | Value | Artifact |
|---|---:|---|
| PC1 aligns with assistant-axis direction | 0.802310 | `research/CLAIMS_REGISTER.md` |
| Reading-based blinded rater objective-certainty correlation with PC1 | Pearson r=0.558; Spearman r=0.565 | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md` |
| Reading-based expanded score model CV R2 for PC1 | 0.616 | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md` |
| Professional objective-certainty correlation with PC1 | Pearson r=0.394; Spearman r=0.422 | `research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md` |
| Sparse external-standard vocabulary PC1 regression R2 | 0.781 | `research/outputs/pc1_competing_theories_test/pc1_competing_theories_report.md` |
| Sparse external-standard incremental R2 over cluster/length controls | +0.0071 | `research/outputs/pc1_competing_theories_test/pc1_competing_theories_report.md` |
| Coordinate-blind external-standard-accountability rating PC1 R2 | 0.704274 | `research/outputs/blind_pc_interpretation_rating_benchmark/benchmark_comparison.csv` |
| PC1 accountability vs determination experiment | mean B-A PC1=+3.297; 5/5 pairs pass | `research/outputs/pc1_accountability_validation/accountability_validation_report.md` |
| PC1 accountability vs arithmetic/checking experiment | mean B-A PC1=+9.551; 5/5 pairs pass | `research/outputs/pc1_accountability_validation/accountability_validation_report.md` |
| Run 2 PC1+ replacement relative to bare Qwen | 7/10 prompts pass; family mean dPC1=+4.025 | `research/outputs/no_label_elicitation_run2/run2_report.md` |
| Run 2 PC1 minimal pairs | 1/5 pairs pass | `research/outputs/no_label_elicitation_run2/run2_report.md` |

### Interpretation

Observed:

- High-PC1 roles include auditor, examiner, evaluator, validator, statistician, screener, lawyer, researcher, reviewer, and grader in professional inventories.
- External-standard-accountability ratings directly recover PC1 better than sparse vocabulary counts.
- Accountability/scrutiny prompt variants move Qwen response activations more positive on PC1 than determination-only or arithmetic/checking variants.

Inferred:

- PC1 is better described by external accountability to standards, admissibility, compliance, review, certification, and disciplined evaluative competence than by general neatness or simple arithmetic.
- Minimal directive-clause swaps are insufficient; scenario-level accountability structure matters.

Speculative:

- PC1 may reflect an answer-space constraint or admissibility geometry in which externally specified standards reduce response-state degrees of freedom.

### Rejected Interpretations

| Rejected interpretation | Reason rejected | Supporting artifact |
|---|---|---|
| orderliness / neatness / symmetry as primary PC1 | Sparse orderliness vocabulary added only +0.0003 R2 over cluster/length controls and was weaker than external-standard accountability. | `research/outputs/pc1_competing_theories_test/pc1_competing_theories_report.md` |
| determination-only PC1 | Sparse determination vocabulary had negative incremental R2 over controls (-0.0023); Run 2 PC1 determination minimal pairs passed only 1/5; accountability variants outperformed determination variants in 5/5 pairs. | `research/outputs/pc1_competing_theories_test/`; `research/outputs/no_label_elicitation_run2/`; `research/outputs/pc1_accountability_validation/` |
| arithmetic/checking alone | Accountability/scrutiny variants outperformed arithmetic/checking variants in 5/5 pairs with mean B-A PC1=+9.551. | `research/outputs/pc1_accountability_validation/accountability_validation_report.md` |
| literal assistantness as the whole axis | Assistant centroid is high PC1 but not the maximum; role rankings and accountability evidence identify a broader standards/evaluation basin. | `research/outputs/assistant_centroid_provenance_audit/`; `research/CLAIMS_REGISTER.md` |

### Caveats

- PC1 remains entangled with assistantness, professional competence, expertise, conscientiousness, and prompt-register effects.
- The old Big Five overlay is partially activation-dependent; use same-space Big Five only with caveats.
- Run 1 PC1-positive prompts failed completely relative to the assistant centroid.
- Run 2 PC1+ replacement passed relative to bare Qwen but failed relative to the assistant role centroid.

### Evidence Supporting Interpretation

- `research/outputs/blind_pc_interpretation_rating_benchmark/`
- `research/outputs/pc1_accountability_validation/`
- `research/outputs/pc1_competing_theories_test/`
- `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`
- `research/q2_stability/qwen/outputs/professional_hierarchy_validation/`
- `research/outputs/no_label_elicitation_run2/`

### Evidence Contradicting Interpretation

- Run 1 PC1-positive family: 0/10 prompt means passed relative to assistant centroid.
- Run 2 PC1 minimal pairs: 1/5 pairs passed.
- Sparse vocabulary evidence is weak after cluster/text controls.
- Intelligence/expertise can outpredict objective certainty in the reading-based rater study.

### Current Evidential Status

- Supported as external-standard accountability / disciplined evaluative competence.
- Tentative as a deeper convergence-pressure / degrees-of-freedom mechanism.

### Cross-Axis Structural Finding: PC1-PC2 Diagonal

Observed:

- The PC1 x PC2 plane has a sparse/forbidden high-PC1/high-PC2 region in current geometry inspections.
- In the PC1 accountability intervention experiment, all 10 accountability/scrutiny manipulations also moved PC2 negative. The pairwise PC2 side effect was 10/10 in the negative direction: mean B-A PC2=-8.665 versus determination and mean B-A PC2=-16.050 versus arithmetic/checking.
- Source artifact: `research/outputs/pc1_accountability_validation/accountability_validation_report.md`.

Inferred:

- For outputs to be accountable to an external standard, the standard must exist in something persistent rather than purely immediate.
- Persistent external standards align with negative-PC2 structure/integration.
- Therefore high-PC1 accountability tends to imply lower PC2.

Caveat:

- This supports or is consistent with a PC1-PC2 diagonal constraint; it does not prove that high PC1 causally requires low PC2 in all contexts.

## 5. Current PC2 Interpretation

Current wording:

- PC2: situated/formative/context-reactive organization versus integrated/stable/abstract/whole-system organization. Lower PC2 corresponds to integration/coherence/abstraction; higher PC2 corresponds to situated immediacy, vulnerability, developmental/formative state, or local social exposure.

### Observed Findings

| Finding | Value | Artifact |
|---|---:|---|
| Conditional PC1-band abstraction correlation with PC2 | r=-0.618; R2=0.382 | `research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md` |
| Conditional coherent-action correlation with PC2 | r=+0.427; R2=0.182 | `research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md` |
| Conditional uncertainty-exposure correlation with PC2 | r=-0.026; R2=0.001 | `research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md` |
| Reading-based rater coherent-action correlation with PC2 | r=0.373 | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md` |
| Reading-based abstraction correlation with PC2 | r=-0.655 | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md` |
| Professional coherent-uncertainty correlation with PC2 | r=-0.007 | `research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md` |
| Muted-PC1 band selected | PC1 45-55 percentile; n=27 | `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_extremes_report.md` |
| Muted-PC1 high PC2 examples | amateur, influencer, patient, gamer, optimist, podcaster, blogger, workaholic, chameleon, caregiver | `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_extremes_report.md` |
| Muted-PC1 low PC2 examples | hive, philosopher, purist, traditionalist, composer, healer, symbiont, visionary, merchant, guardian | `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_extremes_report.md` |
| Cluster-conditioned expected-direction checks | 7/8 global; 5/8 cluster-relative | `research/outputs/pc2_cluster_conditioned_extremes/pc2_cluster_conditioned_extremes_report.md` |
| Coordinate-blind signed integration/coherence PC2 R2 | 0.423010 | `research/outputs/blind_pc_interpretation_rating_benchmark/benchmark_comparison.csv` |
| Run 1 PC2-positive family | 10/10 pass | `research/outputs/no_label_elicitation_validation/no_label_elicitation_validation_report.md` |
| Run 1 PC2-negative family | 5/10 pass | `research/outputs/no_label_elicitation_validation/no_label_elicitation_validation_report.md` |
| Run 2 PC2-negative replacement relative to bare Qwen | 9/10 pass; family mean dPC2=-15.849 | `research/outputs/no_label_elicitation_run2/run2_report.md` |
| Run 2 PC2 minimal pairs | 5/5 pass | `research/outputs/no_label_elicitation_run2/run2_report.md` |

### Interpretation

Observed:

- Low-PC2 roles include crystalline, ascetic, eldritch, mystic, avatar, oracle, leviathan, echo, spirit, ancient globally; within central PC1, hive/philosopher/purist/traditionalist and similar roles are low.
- High-PC2 roles include teenager, adolescent, toddler, procrastinator, gossip, comedian, fool, infant, daredevil, cynic globally; within central PC1, amateur/influencer/patient/gamer/optimist and similar roles are high.
- Run 2 integrative-whole prompts moved negative on PC2 robustly relative to bare Qwen.

Inferred:

- PC2 is not primarily uncertainty exposure.
- Coherent action under uncertainty is a secondary behavioral expression, not the primary axis.
- Negative PC2 is better captured by integration/coherence/abstraction/whole-system continuity.
- Positive PC2 is better captured by situated, formative, reactive, or locally exposed response organization.

Speculative:

- PC2 may encode admissibility constraints: some roles cannot coherently occupy deep integrated abstraction because their role structure is formative, vulnerable, or immediate.

### Rejected Interpretations

| Rejected interpretation | Reason rejected | Supporting artifact |
|---|---|---|
| uncertainty exposure as primary PC2 | Conditional correlation r=-0.026 and R2=0.001 after PC1 control. | `research/q2_stability/qwen/outputs/pc2_conditional_validation/` |
| coherent-action-under-uncertainty as primary PC2 | Weaker than abstraction in conditional validation; professional subset r=-0.007. | `research/q2_stability/qwen/outputs/pc2_conditional_validation/`; `research/q2_stability/qwen/outputs/professional_hierarchy_validation/` |
| archivist/history/preservation-only PC2 | Low PC2 includes abstraction, systemic integration, world-model structure, craft/procedural continuity, and mythic/spiritual integration beyond archive/history cases. | `research/outputs/pc2_muted_pc1_extremes/`; `research/outputs/pc2_cluster_conditioned_extremes/` |
| pure plasticity versus rootedness | Shapeshifter is low PC2 globally and within cluster; chameleon is high globally but below grounded_social cluster median; elder is low globally but high within mythic_spiritual. | `research/outputs/pc2_cluster_conditioned_extremes/pc2_cluster_conditioned_extremes_report.md` |

### Caveats

- PC2 is the least settled of the first three PCs.
- Cluster context changes interpretation of some diagnostic roles.
- Run 1 PC2-negative prompts were weak relative to assistant centroid.
- Trait-profile and same-space trait evidence are activation-derived, not independent psychological ratings.
- PC2 is partly transferable across Qwen/Llama as subspace/topology, not necessarily as same-index PC2.

### Evidence Supporting Interpretation

- `research/q2_stability/qwen/outputs/pc2_conditional_validation/`
- `research/outputs/pc2_muted_pc1_extremes/`
- `research/outputs/pc2_cluster_conditioned_extremes/`
- `research/outputs/pc2_trait_stratified_profile/`
- `research/outputs/blind_pc_interpretation_rating_benchmark/`
- `research/outputs/no_label_elicitation_run2/`

### Evidence Contradicting Interpretation

- Shapeshifter, chameleon, and elder are counterexamples to simplified plasticity/rootedness wording.
- Professional coherent-uncertainty rating fails to predict PC2.
- Run 1 PC2-negative integrated-abstraction family passed only 5/10 prompts.

### Current Evidential Status

- Supported as abstraction/integration/developmental structure.
- Tentative as integrated-abstraction / situated-immediacy with admissibility constraints.

## 6. Current PC3 Interpretation

Current wording:

- PC3: intervention/perturbation/internal-objective pressure versus care/repair/stabilization.

### Observed Findings

| Finding | Value | Artifact |
|---|---:|---|
| Perturbation-stabilization global Pearson vs PC3 | r=0.529 | `research/outputs/pc3_validation/pc3_validation_report.md` |
| Perturbation-stabilization global Spearman vs PC3 | r=0.511 | `research/outputs/pc3_validation/pc3_validation_report.md` |
| Cluster-controlled Pearson vs PC3 | r=0.491 | `research/outputs/pc3_validation/pc3_validation_report.md` |
| Within-cluster pairwise ordering accuracy | 0.773 | `research/outputs/pc3_validation/pc3_validation_report.md` |
| Reading-based rater PC3 correlation | r=0.690 | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md` |
| Reading-based PC3 matched-pair accuracy | 0.950 | `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_axis_rater_report.md` |
| Coordinate-blind internal-objective-vs-care PC3 R2 | 0.393496 | `research/outputs/blind_pc_interpretation_rating_benchmark/benchmark_comparison.csv` |
| Joint three-rating PC3 R2 | 0.462580 | `research/outputs/blind_pc_interpretation_rating_benchmark/benchmark_comparison.csv` |
| Professional system-perturbation correlation with PC3 | r=0.319 | `research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md` |
| Run 1 PC3-positive family | 9/10 pass | `research/outputs/no_label_elicitation_validation/no_label_elicitation_validation_report.md` |
| Run 1 PC3-negative family | 9/10 pass | `research/outputs/no_label_elicitation_validation/no_label_elicitation_validation_report.md` |
| Run 2 PC3 cost-to-others minimal pairs | 3/4 complete pairs pass in run report; 4/5 pass when Run 1 `pc3_pos_05` is included as pair 1 A-side in diagnostics | `research/outputs/no_label_elicitation_run2/`; `research/outputs/no_label_elicitation_run2_prompt_diagnostics/` |
| Frozen strict Agreeableness direction vs Qwen PC3 loading | cosine=-0.847133 | `research/outputs/externally_anchored_big_five/big_five_pc_direction_cosines.csv` |
| Strict Agreeableness role scores vs Qwen PC3 | Pearson r=-0.881714; Spearman rho=-0.837526; R²=0.777420 | `research/outputs/externally_anchored_big_five/agreeableness_pc3_focal_test.json` |
| Strict Agreeableness conditional contribution | standardized beta=-0.894047; held-out partial R²=0.524122 | `research/outputs/externally_anchored_big_five/big_five_partial_r2.csv` |

### Interpretation

Observed:

- Positive PC3 includes both prosocial interventionist roles (auditor, debugger, skeptic, statistician, lawyer) and antisocial/disruptive roles (demon, parasite, criminal, smuggler).
- Negative PC3 includes counselor, therapist, healer, caregiver, angel, mediator.
- Negative Qwen PC3 strongly aligns with a frozen externally anchored activation-derived Agreeableness direction at both direction and role-score levels.
- Cost-to-others framing usually moves more positive on PC3 than cost-to-self framing.
- Minimal-pair evidence showed cost-to-others framing moves PC3 positive more than cost-to-self framing.

Inferred:

- PC3 is not moral valence.
- PC3+ is not merely willingness to incur cost.
- PC3+ is more specifically willingness to impose costs on others in pursuit of an internal objective.
- PC3- is identity organized around the wellbeing of others rather than an internal objective.
- Positive PC3 is better described as intervention, stress-testing, disruption, exploitation, challenge, or internal-objective pressure.
- Negative PC3 is better described as care, repair, protection, mediation, preservation, and stabilization.
- Agreeableness is a strong component of negative Qwen PC3, but is not equivalent to the full axis.

Speculative:

- Cost-to-self prompts may evoke sacrifice/duty/endurance, which can pull toward negative PC3 or off-axis PC1/PC2 regions.

### Rejected Interpretations

| Rejected interpretation | Reason rejected | Supporting artifact |
|---|---|---|
| PC3 as pure moral badness | Moral badness control was much weaker than perturbation-stabilization; prosocial perturbative roles are high PC3. | `research/outputs/pc3_validation/pc3_validation_report.md` |
| PC3 as professionalism | Professionalism control was weak; high-PC3 examples include both professional and nonprofessional roles. | `research/outputs/pc3_validation/pc3_validation_report.md` |
| PC3-positive as only harmfulness | Auditor/debugger/skeptic/statistician/lawyer can be positive PC3 without being harmful. | `research/outputs/pc3_validation/pc3_validation_report.md` |
| cost-to-self as PC3-positive | `pc3_pos_05` moved primarily negative PC1 and positive PC2, not positive PC3; cost-to-others minimal-pair framing performed better. | `research/outputs/no_label_elicitation_geometry_diagnostics/`; `research/outputs/no_label_elicitation_run2_prompt_diagnostics/` |

### Caveats

- Grounded_social within-cluster PC3 performance is weak.
- Agreeableness does not occupy the same model-local PC number across systems: Llama aligns mainly with PC2, while Gemma's PC3 result is weaker and mixed with PC1.
- The externally anchored construction remains same-space activation evidence with correlated domain directions; it is not independent human psychometric validation.
- Professional subset includes high-PC3 technical/institutional counterexamples not rated strongly perturbative.
- Negative controls are not inert.
- No-label PC3 movement has substantial off-axis coupling, especially with PC1.

### Evidence Supporting Interpretation

- `research/outputs/pc3_validation/`
- `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`
- `research/outputs/blind_pc_interpretation_rating_benchmark/`
- `research/outputs/no_label_elicitation_validation/`
- `research/outputs/no_label_elicitation_run2_prompt_diagnostics/`

### Evidence Contradicting Interpretation

- Grounded_social within-cluster pairwise accuracy in PC3 validation was 0.565.
- Professional subset counterexamples include economist, mathematician, statistician, and lawyer for simple perturbation wording.
- Run 2 PC3 pair 3 failed.

### Current Evidential Status

- Provisionally supported.
- Stronger than PC2 in direct rater evidence; still not settled as a single clean axis.

## 7. No-Label Elicitation Program

### Run 1

| Item | Observed finding | Artifact |
|---|---|---|
| Frozen source | 60-prompt packet from `research/outputs/no_label_elicitation_prompt_packet_v1/` | `research/outputs/no_label_elicitation_validation/no_label_elicitation_validation_report.md` |
| Design | 6 families x 10 prompts x 10 independent generations = 600 planned responses | same |
| Completion | 600/600 responses; zero reported error rows | same |
| Blinding | Qwen saw only `prompt_text`; no PC labels, polarity labels, family labels, reasoning, metadata, or predictions | same |
| Independence | Fresh one-message conversation; no prior prompts/responses; no cross-sample `past_key_values`; separate no-cache extraction pass | same |
| Success threshold | 70% of prompt means per family in target direction | same |
| Family pass/fail | PC1- 10/10 pass; PC1+ 0/10 fail; PC2- 5/10 fail; PC2+ 10/10 pass; PC3- 9/10 pass; PC3+ 9/10 pass | same |

### Run 1 Geometry Diagnostics

| Item | Observed finding | Artifact |
|---|---|---|
| Assistant centroid | PC1=33.703, PC2=3.442, PC3=-5.156 | `research/outputs/no_label_elicitation_geometry_diagnostics/no_label_elicitation_geometry_diagnostics_report.md` |
| Assistant percentile | PC1=83.3, PC2=64.0, PC3=36.0 among Qwen role centroids | same |
| PC1+ failure | Family mean moved PC1=-53.055 relative to assistant; mean PC1=-19.352 | same |
| PC3-negative off-axis | Family mean moved PC1=-95.868 and PC3=-13.243 | same |
| `pc3_pos_05` | dPC1=-88.495, dPC2=+41.486, dPC3=-0.598 | same |

### Assistant Centroid Provenance

| Item | Observed finding | Artifact |
|---|---|---|
| Centroid source | Released Qwen `assistant` role/persona vector selected from reconstructed canonical role coordinates | `research/outputs/assistant_centroid_provenance_audit/assistant_centroid_provenance_report.md` |
| Bare-Qwen answer | No; not a measurement of bare Qwen | same |
| Default-vector answer | No; not `default_vector.pt` | same |
| Assistant-axis answer | No; not `assistant_axis.pt` | same |
| Run 2 implication | 240-question bare-Qwen baseline is foundational for future no-label interpretation | same |

### Run 2

| Item | Observed finding | Artifact |
|---|---|---|
| Design | 289 catalog rows; 1,690 planned generations | `research/outputs/no_label_elicitation_run2/run2_report.md` |
| Completion | 1,690/1,690 responses; 0 errors; 0 empty responses; 1,690 activation shards | same |
| Baseline | Bare-Qwen 240 extraction questions x 5 samples = 1,200 baseline generations | same |
| Bare-Qwen centroid | PC1=23.510, PC2=14.041, PC3=-2.460 | same |
| Assistant role centroid | PC1=33.703, PC2=3.442, PC3=-5.156 | same |
| PC1+ replacement | 7/10 pass relative to bare Qwen; 3/10 pass relative to assistant centroid | same |
| PC2- replacement | 9/10 pass relative to bare Qwen; 8/10 pass relative to assistant centroid | same |
| PC3 cost-to-others minimal pairs | 3/4 complete pairs pass in run report | same |
| PC1 minimal pairs | 1/5 pass | same |
| PC2 minimal pairs | 5/5 pass | same |

### Prompt Redesigns / Diagnostics

| Item | Observed finding | Artifact |
|---|---|---|
| PC1+ strongest prompts | access-control, signature-control, grant-rule admissibility scenarios | `research/outputs/no_label_elicitation_run2_prompt_diagnostics/run2_prompt_diagnostics_report.md` |
| PC1+ failures | spreadsheet arithmetic, equipment timing, training completion prompts | same |
| PC2- strongest prompts | craft guild identity and forest recovery organization | same |
| PC2- failure | neighborhood prompt invited local place/social description | same |
| PC3 cost-to-others | 4/5 pass when Run 1 A-side is included for pair 1 | same |

## 8. Interpretations Explicitly Rejected

| Axis | Rejected interpretation | Reason rejected | Supporting artifact |
|---|---|---|---|
| PC1 | orderliness | Sparse orderliness vocabulary adds almost no signal over controls; accountability evidence is stronger. | `research/outputs/pc1_competing_theories_test/` |
| PC1 | neatness | Same as orderliness; not supported as the primary axis. | `research/outputs/pc1_competing_theories_test/` |
| PC1 | symmetry | No current strong evidence identifies symmetry as primary; accountability/intervention evidence supersedes it. | `research/outputs/pc1_competing_theories_test/`; `research/outputs/pc1_accountability_validation/` |
| PC1 | determination-only | Determination vocabulary and minimal pairs fail or underperform; accountability/scrutiny variants are stronger. | `research/outputs/no_label_elicitation_run2/`; `research/outputs/pc1_accountability_validation/` |
| PC1 | arithmetic/checking alone | Accountability/scrutiny outperforms arithmetic/checking in matched scenarios. | `research/outputs/pc1_accountability_validation/` |
| PC2 | uncertainty exposure | Conditional PC1-band validation gives r=-0.026 and R2=0.001. | `research/q2_stability/qwen/outputs/pc2_conditional_validation/` |
| PC2 | coherent action under uncertainty as primary | Weaker than abstraction/integration; professional hierarchy result fails. | `research/q2_stability/qwen/outputs/pc2_conditional_validation/`; `research/q2_stability/qwen/outputs/professional_hierarchy_validation/` |
| PC2 | archivist-only / preservation-only | Low-PC2 region includes abstract, systemic, mythic, formal, and whole-system roles beyond archives. | `research/outputs/pc2_muted_pc1_extremes/`; `research/outputs/pc2_cluster_conditioned_extremes/` |
| PC2 | simple plasticity axis | Shapeshifter/chameleon/elder counterexamples break simple plasticity/rootedness wording. | `research/outputs/pc2_cluster_conditioned_extremes/` |
| PC3 | moral badness | Negative control is weaker; prosocial perturbative roles are high PC3. | `research/outputs/pc3_validation/` |
| PC3 | professionalism | Professionalism negative control is weak and not explanatory. | `research/outputs/pc3_validation/` |
| PC3 | harmfulness-only | High-PC3 includes auditor/debugger/skeptic/statistician/lawyer. | `research/outputs/pc3_validation/` |
| PC3 | cost-to-self pressure | Cost-to-self wording produced off-axis/self-sacrifice behavior; cost-to-others contrast is better. | `research/outputs/no_label_elicitation_geometry_diagnostics/`; `research/outputs/no_label_elicitation_run2_prompt_diagnostics/` |

## 9. Open Questions

Active unresolved questions only:

| ID | Open question | Current basis |
|---|---|---|
| OQ1 | Can SVD15 lexical/register signal be distilled into stable human-readable residual dimensions? | SVD15 mean R2=0.707; abstract hand features lag behind. |
| OQ2 | Does independent human or second-model rating replicate the GPT-5.5 blinded rater evidence? | Current rater studies use GPT-5.5/Codex, not human panels. |
| OQ3 | How should PC2 be worded without over-compressing abstraction, integration, maturity, context-reactivity, and cluster effects? | PC2 remains compound and counterexample-sensitive. |
| OQ4 | Can PC1 accountability structure be made robust across broader no-label scenarios without large off-axis PC2/PC3 shifts? | PC1 accountability validation succeeds, but minimal pairs and assistant-centroid contrast remain caveats. |
| OQ5 | Which no-label elicitation results should be included in the main paper versus appendix? | Run 2 is strong for PC2 and accountability follow-up; Run 1 failures require careful framing. |
| OQ6 | How much of Big Five predictive performance reflects partially activation-dependent provenance? | Old Big Five overlay is cluster-conditioned; same-space replacement is activation-derived but not independent psychometrics. |
| OQ7 | Should local activation-cloud geometry be included as supporting Paper 1.5 evidence or reserved for Paper 2? | Current state recommends Paper 2/local-manifold framing, with limited Paper 1.5 support for centroids-as-distributions. |
| OQ8 | Does a frozen complete trait-profile prediction match the observed coordinate of a genuinely new behaviorally elicited Qwen persona? | V1 same-space predictor and OOD/error references are complete; behavioral realization was deliberately not run in this stage. |
| OQ9 | What, if anything, should follow inspection of the frozen correlation-defined Qwen-family to SAPA measurement inventory? | The inventory exposes 37 construct/item candidates and 350 items across 12 signed families, but this task deliberately selected no subsequent experiment and ran no respondent scoring or correspondence analysis. |
| OQ10 | Does AA-7 aligned-direction recurrence generalize beyond the three saved-vector releases and the common 275 English role inventory? | Current alignment is strong but can reflect shared role-instruction structure; independent role inventories and model releases are untested. |

## 10. Claims Inventory

Status mapping:

- `established`: stable observed/source result or strong project foundation.
- `supported`: current CLAIMS_REGISTER status is Supported or Provisionally Supported.
- `tentative`: current CLAIMS_REGISTER status is Tentative or Partially supported.
- `speculative`: current CLAIMS_REGISTER status is Speculative.
- `rejected`: explicitly rejected in this ledger.

| Claim | CLAIMS_REGISTER status | Ledger status |
|---|---|---|
| Persona Geometry Is Low-Dimensional | Supported | supported |
| Assistant Axis Aligns Strongly With PC1 | Observed | established |
| Careful Evaluator Occupies a Privileged Basin | Supported | supported |
| Base Models Already Contain Persona Geometry | Supported | supported |
| RLHF Primarily Reweights Existing Persona Geometry | Tentative | tentative |
| Big Five-Style Features Predict Activation PCA Better Than Semantic Baseline | Observed | established |
| Procedural Features Independently Predict Meaningful Geometry | Supported | supported |
| Hierarchical Trait-to-Procedural Model Improves Prediction | Supported | supported |
| Residual Manifold Features Add a Small Diagnostic Layer | Tentative | tentative |
| Residual SVD Structure Strongly Improves Prediction | Observed | established |
| Semantic Topology Partially Predicts Activation Geometry | Supported | supported |
| Explicit Role-Label Exposure Is a Methodological Caveat | Observed | established |
| No-Label Prompt Semantic Topology Mostly Survives Label Removal | Supported | supported |
| PC1 Tracks Constraint, Standards, Expertise, and Procedural Competence | Supported | supported |
| PC2 Is an Abstraction/Integration/Developmental Axis, Not Simple Uncertainty Capacity | Supported | supported |
| PC3 Tracks Cooperative-Stabilizing Versus Antagonistic-Transgressive Stance | Provisionally Supported | supported |
| Persona Space May Exhibit Cone-Like Geometric Constraints | Speculative | speculative |
| Cone Boundaries Represent Genuine Geometric Limits | Speculative | speculative |
| Adaptive Extraction Is Operationally Validated for Trickster | Observed | established |
| Persona Drift Can Be Monitored Geometrically | Supported | supported |
| Trait-Vector Geometry Predicts Persona PCA Location | Observed | established |
| Direct Trait-Space PCA Partially Reorganizes Persona-Space Interpretations | Tentative | tentative |
| Released Trait Prompt Artifacts Enable Prompt-To-Geometry Forecasting | Observed | established |
| Prompt Text Forecasts Geometry On Held-Out Concepts | Supported | supported |
| PC1 Is A Convergence-Pressure / Degrees-Of-Freedom Axis | Tentative | tentative |
| PC2 Is An Integrated-Abstraction / Situated-Immediacy Axis With Admissibility Constraints | Tentative | tentative |
| Cluster Conditioning Improves Calibrated PC1/PC2 Prediction But Not Simple Within-Cluster Pairwise Judging | Supported | supported |
| Novel Prompt Battery Is H100-Ready Under Percentile-Edge Criteria | Observed | established |
| Pre-H100 Validation Preparation Is Complete | Observed | established |
| Novel Prompt-To-Geometry Forecasts Generalize To Measured Response Activations | Supported | supported |
| H100 Forecast Errors Are Regionally Structured And Calibration-Limited | Supported | supported |
| Public-Source Audit Found Likely H100 Extraction Boundary Mismatch | Observed | established |
| Percentile-Edge Prompt Battery Shows Stress-Test Bias | Supported | supported |
| H100 Error Pattern Is Not Native To The Frozen Role-Artifact Forecaster | Supported | supported |
| Public Role Rollout Artifacts Allow Input Reconstruction But Not Success Filtering | Observed | established |
| H100 Anomaly Interpretation Is Governed By Four Methodological Dependency Tracks | Supported | supported |
| Within-Role Displacement Study Design Is Prepared | Observed | established |
| Playwright Within-Role Displacement Scoring Is Prepared | Observed | established |
| Frozen No-Label Elicitation Prompts Partially Validate Directional Activation Movement | Partially supported | tentative |
| Activation-Derived Trait Directions Recur in Aligned Model Role-Score Subspaces | Observed | established with model-only boundary |
| PC1 orderliness/neatness/symmetry primary interpretation | rejected in this ledger | rejected |
| PC1 determination-only interpretation | rejected in this ledger | rejected |
| PC2 uncertainty-exposure primary interpretation | rejected in this ledger | rejected |
| PC2 archivist-only interpretation | rejected in this ledger | rejected |
| PC3 moral-badness interpretation | rejected in this ledger | rejected |

## 11. Paper Inclusion Recommendations

### Recommended for main paper

| Item | Justification |
|---|---|
| Benchmark progression from semantic baseline through SVD15 | Core evidence for layered interpretation and predictive progression. |
| Big Five provenance caveat and same-space replacement | Required to prevent overclaiming psychometrics. |
| Blind PC interpretation rating benchmark | Direct compact test of PC interpretations under coordinate blinding. |
| PC1 accountability validation | Latest focused evidence for PC1 wording beyond orderliness/determination/checking. |
| PC2 conditional validation | Central evidence that PC2 is abstraction/integration/developmental, not uncertainty exposure. |
| PC2 muted-PC1 and cluster-conditioned diagnostics | Necessary caveats and counterexamples for PC2 wording. |
| PC3 perturbation-stabilization validation | Best direct evidence for PC3 wording and moral-valence rejection. |
| Externally anchored Big Five audit | Strong frozen-mapping evidence that negative Qwen PC3 has an Agreeableness-related component; include exact direction/role statistics and the cross-model non-identity caveat. |
| Assistant centroid provenance and bare-Qwen baseline distinction | Required methodological correction for no-label interpretation. |
| Run 2 no-label core results | Useful activation-space support, especially bare-Qwen baseline, PC2 replacement/minimal pairs, and PC1 accountability context. |

### Recommended for appendix

| Item | Justification |
|---|---|
| AA-7 frozen-trait efficiency and aligned-subspace convergence | Include as bounded supporting/appendix evidence, not a headline: the primary human-selection efficiency result is negative, while the strong aligned Big Five/human-direction recurrence qualifies AA-2/AA-3 and requires shared-role/model-only caveats. A short main-text sentence may point to the appendix if cross-model organization is discussed. |
| Run 1 no-label prompt packet and failures | Important negative/diagnostic evidence; too detailed for main narrative. |
| No-label geometry diagnostics | Explains PC1-positive and `pc3_pos_05` failure modes; appendix evidence. |
| Run 2 prompt-level diagnostics | Useful for prompt design and exact prompt examples; appendix table. |
| Professional hierarchy validation | Supports PC1/PC3 and weakens PC2 coherent-uncertainty interpretation; subset-specific. |
| Blinded axis rubric validation | Conservative lexical/proxy screen; mainly a limitation and motivation for richer rater studies. |
| Trait-profile provenance audit | Required technical provenance; too detailed for main flow. |
| Trait-profile PC predictor held-out generalization and Llama/Gemma replication | Stronger LOPO/family/permutation/synthetic support for the same-space trait-geometry statement across three saved vector sets; include with explicit basis-coverage, PC-semantic, and no-behavioral-validation caveats. |
| Qwen trait sparsity and basis-coverage audit | Essential qualification of the complete-trait predictor: compact real traits are unusually efficient, while the 240-trait near-ceiling result is substantially generic high-dimensional basis coverage. |
| Big Five provenance audit details | Main paper needs conclusion; full dependency details belong in appendix. |
| Residual manifold and SVD component details | Main paper can cite metrics; component-level detail belongs in appendix. |

### Recommended to exclude

| Item | Justification |
|---|---|
| H100/A100 forecast-observed validation as core Paper 1.5 evidence | Separate execution-time validation and extraction-boundary diagnostics; not core interpretive ledger. |
| Prompt-battery generation details | Useful project history but not needed for Paper 1.5 interpretation. |
| RunPod logs and activation shards | Reproducibility/support artifacts, not writing content. |
| Occupation-population joins and overlays | Exploratory future-work/appendix material only; not core evidence. |
| SAPA/NLSY97 feasibility audit, occupational-centroid stability study, provisional/narrow bridge, human-only SAPA structure audit, Qwen-derived construct source, and correlation-defined family inventory as Paper 1.5 model results | Use only as carefully bounded future-work context; the narrow audit contracts the direct bridge to 9 high + 3 moderate links, the broader inventory exposes available constructs/items for numerical Qwen families, and AA-5 identifies selected stable cells. None establishes construct equivalence, model correspondence, or a respondent-scoring solution, none belongs in the model-geometry evidence chain, and the family-inventory task deliberately selected no next experiment. |
| Adaptive extraction operational details beyond brief caveat | Methodological due diligence; not the headline contribution. |
| Speculative local activation-cloud Paper 2 claims | Future scope; only use if explicitly framed as distributional motivation. |
