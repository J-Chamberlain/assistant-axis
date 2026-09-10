# PC-Ranked Persona Trait Profiles

Date: 2026-09-09 (America/Los_Angeles)
Status: completed descriptive visualization; no new activation experiment.
Startup: canonical raw STARTUP_MANIFEST, RESEARCH_STATE, THREAD_START and CLAIMS_REGISTER fetched in order; hashes, byte counts and local copies verified before work.
Branch: master. Base commit: bcba251e6cee617e5b01af62c99c4d05028d92db.

## Open the Plots

Open [persona_trait_ridges.html](persona_trait_ridges.html), the completed offline artifact. It contains all 275 personas in each of three plots, descending PC1, PC2 and PC3, respectively. Click a persona name or select it above the plots to locate it in every ranking. Headers stay visible while scrolling. Wide displays show three columns; smaller displays stack them, with horizontal scrolling where needed to preserve legible labels. The graphs are pre-rendered and remain visible even without JavaScript. No external chart dependency or data fetch is needed.

Full all-persona figures: [PC1 SVG](persona_trait_ridges_pc1.svg), [PC2 SVG](persona_trait_ridges_pc2.svg), [PC3 SVG](persona_trait_ridges_pc3.svg); matching PNGs are in the same directory. [Overview](persona_trait_ridges_overview.png) deliberately shows only the first 15 personas per PC, not the full population. The working emotion ridge plots and 3D surface viewer are unchanged.

## Selection and Left-to-Right Order

Fifteen traits form a manageable editorial coverage sample from the existing 240 traits, not a statistically representative or optimized subset. Selection and grouping use the saved descriptions, not a search for large PC correlations or attractive ridges. We include expressive/conceptual, situated, evaluative, oppositional and prosocial tendencies rather than only assistant-like traits. The group names are reading aids, not discovered factors, fitted clusters, Big Five dimensions or valence labels.

| Position | Group | Trait | Saved description (verbatim) |
|---|---|---|---|
| 1 | Exploration | creative | Offers imaginative solutions, novel perspectives, and original approaches to problems. |
| 2 | Exploration | abstract | Thinks in terms of concepts, patterns, and theoretical frameworks. |
| 3 | Exploration | curious | Shows genuine interest in learning and exploring new topics and ideas. |
| 4 | Response | reactive | Responds to situations as they arise rather than planning ahead. |
| 5 | Response | adaptable | Adjusts communication style and approach based on context and user needs. |
| 6 | Response | practical | Emphasizes real-world applications and actionable advice over theory. |
| 7 | Scrutiny | skeptical | Questions assumptions, seeks evidence, and challenges conventional thinking. |
| 8 | Scrutiny | analytical | Breaks down complex topics into logical components and examines each part systematically. |
| 9 | Scrutiny | conscientious | Demonstrates careful attention to responsibilities and thoroughness in work. |
| 10 | Challenge | rebellious | Challenges authority and conventional wisdom. Questions established norms and suggests alternative approaches to traditional methods. |
| 11 | Challenge | competitive | Emphasizes winning, achievement, and outperforming others. |
| 12 | Challenge | manipulative | Uses deception, emotional exploitation, and psychological tactics to control others. |
| 13 | Affiliation | empathetic | Shows understanding and consideration for human emotions and perspectives. |
| 14 | Affiliation | agreeable | Prioritizes harmony and maintaining positive relationships over confrontation. |
| 15 | Affiliation | altruistic | Prioritizes helping others and societal benefit over individual gain. |

These traits are not ordered negative-to-positive. Traits do not have the same valence interpretation as the emotion channels. Equally spaced categories, dashed group boundaries, colored dots and group titles make the editorial ordering visible. Trait text and the ridge line are neutral. Colors mean only the descriptive group, never assistant-axis projection, score magnitude, goodness or badness. Reordering categories would change the curve's silhouette without changing the underlying scores.

## Source Data and Normalization

Observed sources:

- [Canonical geometry](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/visualizations/geometry_viz_data.json): unchanged `roles.names` and `roles.pca3d`, 275 unique personas, three PCs. No PCA fit or sign change.
- [Primary trait matrix](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv): 275 rows and 241 columns, `persona` plus 240 cosine scores. Selected values are copied exactly, joined by persona, not row position.
- [PC2 analysis joined matrix](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv): all 66,000 trait values compared with the primary matrix; maximum absolute difference 9.985502008591496e-17, consistent with a CSV floating-point round-trip. The primary matrix retains the source precision.
- [Trait definitions](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/data/traits/trait_list.json): 240 names/descriptions; selected definitions copied without relabeling the underlying keys.
- [Matrix generator](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/trait_persona_prediction/run_trait_persona_prediction.py) and [provenance audit](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md): deterministic cosine similarities between L2-normalized means over each released Qwen role/trait tensor's 64 stored rows. We reuse these saved scores, not the single-layer emotion readout.

For each trait independently across all 275 personas:

`height = 100 * (average_rank(raw_cosine) - 0.5) / 275`

Ties use average ranks. The common height scale is 0-100, with observed endpoints inside that interval. Population z-scores use `(raw - mean) / std(ddof=0)`; raw cosine, z-score and percentile are in marker tooltips and the 4,125-row [score CSV](persona_trait_ridge_scores.csv). Each persona has the same 15-value profile in all three rankings. Only row order changes, using descending original PC and alphabetical tie-breaking.

The percentile is a relative position among personas for that trait, not the probability, prevalence or physical intensity of a trait. No per-persona peak scaling, area normalization or softmax is performed. A high peak for one trait and another high peak for a second trait mean high relative rankings in their respective populations; they do not establish equal absolute trait strengths. Low height is not proof of trait absence.

PCHIP connects the categorical percentile values without overshooting. Exact category dots are the data; intermediate curve points are visual interpolation. This is a ridge-shaped profile, not a probability density or continuous latent measurement.

## Evidential Limits

Observed: the profiles are same-space activation-cosine evidence. Mixed provenance means inherited released trait vocabulary/vectors combined with an internally computed cosine matrix. Trait scores were not independently assigned by humans, a questionnaire, or a new LLM judge. The role PCA and trait similarities share released activation sources, so their agreement is not independent psychological validation. Historical metadata saying layer 48 does not change the matrix generator's actual averaging across all 64 stored rows.

Inferred: grouped trait profiles may help manual inspection of how already-mapped tendencies are distributed through PC space. No new PC interpretation is claimed. Unknown: generalization to response-level behavior or independent trait assessments. The selected 15 do not exhaust all 240 dimensions, and traits are not orthogonal.

## Verification and Reproduction

Run from the repository root, with NumPy/SciPy available and Sharp available to Node:

```sh
python3 -B research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py
python3 -B research/outputs/persona_trait_ridge_plots/verify_persona_trait_ridges.py
node research/outputs/persona_trait_ridge_plots/render_ridge_images.cjs
python3 -B research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py --inventory-only
```

Validation: 275 unique personas, 15 selected traits, 4,125 unique score rows, 825 pre-rendered ridge rows, 12,375 category markers, exact canonical geometry, exact primary scores, independently computed percentiles/z-scores, descending ranks and input SHA256 checks. Four SVGs rasterized to nonblank PNGs; overview visually inspected. Node DOM-double tests exercise linked persona selection and clearing. These are data, static-render and unit tests, not live-browser screenshots. Existing viewers were not modified.

Artifacts and canonical raw URLs are enumerated with SHA256 hashes in [artifact_inventory.csv](artifact_inventory.csv). Runtime/source details are in [persona_trait_ridge_manifest.json](persona_trait_ridge_manifest.json); checks in [persona_trait_ridge_checks.json](persona_trait_ridge_checks.json) and [ridge_render_checks.json](ridge_render_checks.json).

No GPU, model generation, new activation extraction, model API or judge calls were performed. CLAIMS_REGISTER and FINDINGS_LEDGER are unchanged because this adds a descriptive view of existing data, not new empirical evidence. No sticky note was directly addressed. Next step: manual inspection, followed by user-selected expansion of the trait subset if useful.
