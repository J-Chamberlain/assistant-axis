# Cross-model PC trait specificity

Date: 2026-09-12  
Status: completed and verified  
Models: Qwen/Qwen3-32B, Llama-3.3-70B, Gemma-2-27B

## Result in one paragraph

The frozen Qwen workflow reproduces exactly (328 PC-associated memberships and 88 strict six-PC-purity markers) and transfers without retuning to the two other saved-vector releases. LLaMA has 274 associated memberships and 122 strict markers; Gemma has 297 and 92. For the focal corresponding role-score directions, Qwen PC2, LLaMA PC1, and Gemma PC2 explain 16.163%, 17.232%, and 12.782% of their respective model-local variance. Qwen and Gemma most clearly recur on situated/experiential/reactive engagement versus inward, solemn, formal, and ritual mediation. LLaMA PC1 supplies a coherent concrete-accessible versus symbolic/abstract contrast, but its large imaginative-expressive negative family also carries Qwen-PC1-like content. It therefore clarifies one decomposition of the plane without isolating a clean one-axis equivalent, consistent with the observed LLaMA PC1/PC2 rotation.

## Frozen method and reproduction gate

The PC-associated rule is unchanged: `|Pearson r| >= .50`, within-PC Benjamini-Hochberg FDR `q < .01`, and sign stability `>= .95` over 2,000 role bootstraps. The per-PC seeds remain `20260913` through `20260918`. The strict rule is also unchanged: original association membership, strict observed target dominance over the other five PCs, 2,000-bootstrap target-dominance probability `>= .95` with seed `20260920`, and six-PC purity `r_target² / sum(r_PC1² ... r_PC6²) >= .70`. No threshold was selected or changed after inspecting LLaMA or Gemma.

The complementary broader specificity layer was preserved using its own frozen seed `20260912`: it yields 202/205/173 target-dominant memberships and 70/105/72 highly concentrated (`purity >= .75`) memberships for Qwen/LLaMA/Gemma. This layer is descriptive and is not substituted for the strict result.

The original Qwen scripts were rerun before generalization. Every required Qwen PC/pole count was recovered exactly:

- Associated: PC1 `+47/-123`, PC2 `+31/-44`, PC3 `+42/-31`, PC4 `+2/-6`, PC5 `+1/-0`, PC6 `+0/-1`; total 328.
- Strict: PC1 `+12/-48`, PC2 `+3/-10`, PC3 `+7/-8`, PC4-PC6 zero; total 88.

## Table 1 — explained variance

Each cell is marginal percentage followed by cumulative percentage through that PC.

| PC | Qwen 3 32B | LLaMA 3.3 70B | Gemma 2 27B |
|---|---:|---:|---:|
| PC1 | 31.595% (31.595%) | 17.232% (17.232%) | 23.453% (23.453%) |
| PC2 | 16.163% (47.759%) | 14.159% (31.391%) | 12.782% (36.235%) |
| PC3 | 8.690% (56.449%) | 6.479% (37.870%) | 5.686% (41.921%) |
| PC4 | 4.520% (60.969%) | 5.252% (43.122%) | 5.327% (47.248%) |
| PC5 | 3.615% (64.584%) | 3.711% (46.833%) | 3.874% (51.122%) |
| PC6 | 2.824% (67.408%) | 3.110% (49.942%) | 3.159% (54.281%) |
| PC1–6 cumulative | 67.408% | 49.942% | 54.281% |

Source: canonical `extended_persona_pca/full_pca_spectrum.csv`; PCA was not recomputed.

## Table 2 — PC-associated trait memberships

Cells are `positive / negative (total)`.

| PC | Qwen | LLaMA | Gemma |
|---|---:|---:|---:|
| PC1 | 47 / 123 (170) | 10 / 78 (88) | 49 / 109 (158) |
| PC2 | 31 / 44 (75) | 73 / 74 (147) | 49 / 49 (98) |
| PC3 | 42 / 31 (73) | 15 / 10 (25) | 19 / 13 (32) |
| PC4 | 2 / 6 (8) | 9 / 4 (13) | 6 / 2 (8) |
| PC5 | 1 / 0 (1) | 0 / 0 (0) | 0 / 0 (0) |
| PC6 | 0 / 1 (1) | 1 / 0 (1) | 0 / 1 (1) |
| **Total memberships** | **328** | **274** | **297** |

## Table 3 — strict axis-specific trait memberships

Cells are `positive / negative (total)`. Purity uses exactly PC1-PC6.

| PC | Qwen | LLaMA | Gemma |
|---|---:|---:|---:|
| PC1 | 12 / 48 (60) | 4 / 33 (37) | 13 / 52 (65) |
| PC2 | 3 / 10 (13) | 40 / 42 (82) | 9 / 16 (25) |
| PC3 | 7 / 8 (15) | 1 / 2 (3) | 1 / 0 (1) |
| PC4 | 0 / 0 (0) | 0 / 0 (0) | 0 / 1 (1) |
| PC5 | 0 / 0 (0) | 0 / 0 (0) | 0 / 0 (0) |
| PC6 | 0 / 0 (0) | 0 / 0 (0) | 0 / 0 (0) |
| **Total memberships** | **88** | **122** | **92** |

## Table 4 — Qwen-referenced role-score correspondence

The values are verified from the canonical role-score analysis and reproduced directly from the shared-role viewer coordinates to maximum absolute error `6.67e-16`. A negative sign is only a pole-orientation flip.

| Qwen PC | Best LLaMA PC | Pearson r | Best Gemma PC | Pearson r | Structural note |
|---|---:|---:|---:|---:|---|
| PC1 | PC2 | -.676 | PC1 | +.953 | Qwen PC1/PC2 and LLaMA PC1/PC2 are partly rotated; one-to-one equivalence is not warranted. |
| PC2 | PC1 | +.692 | PC2 | +.922 | LLaMA PC1 is the best single score correlate but remains mixed with the rotated PC1/PC2 plane. |
| PC3 | PC4 | +.802 | PC3 | +.806 | Strong score recurrence does not guarantee strict trait-marker recurrence. |
| PC4 | PC3 | +.690 | PC4 | -.628 | Gemma pole orientation is reversed. |
| PC5 | PC5 | +.688 | PC5 | -.651 | Gemma pole orientation is reversed. |
| PC6 | PC6 | +.505 | PC8 | -.570 | Gemma’s best match lies outside the requested PC1-PC6 specificity set. |

## Focal evidence packet — Qwen PC2 / LLaMA PC1 / Gemma PC2

### Observed

Qwen PC2 explains 16.163% of Qwen variance. Its strict positive traits are **experiential, practical, inquisitive**; all three are highly concentrated. Its strict negative traits are **introverted, ritualistic, pensive, theoretical, abstract, reverent, conceptual, principled, solemn, erudite**; all except solemn and erudite are highly concentrated.

LLaMA PC1 explains 17.232% of LLaMA variance. Its strict positive traits are **grounded, contemporary, accessible, practical**; grounded, contemporary, and practical are highly concentrated. Its strict negative traits are **ethereal, cryptic, bombastic, grandiose, poetic, spiritual, mystical, theatrical, enigmatic, dramatic, metaphorical, rhetorical, esoteric, romantic, philosophical, melodramatic, eclectic, ascetic, fatalistic, deterministic, creative, meditative, chaotic, whimsical, paradoxical, epicurean, conceptual, historical, artistic, theoretical, abstract, idealistic, innovative**. The highly concentrated negative subset is **ethereal, cryptic, bombastic, grandiose, poetic, spiritual, mystical, theatrical, enigmatic, dramatic, metaphorical, rhetorical, esoteric, romantic, philosophical, melodramatic, eclectic, ascetic, fatalistic, deterministic, creative, chaotic, whimsical, paradoxical, epicurean, historical**.

Gemma PC2 explains 12.782% of Gemma variance. Its strict positive traits are **casual, anxious, impatient, irreverent, flippant, experiential, nonchalant, extroverted, reactive**; the highly concentrated subset is **casual, anxious, impatient, irreverent, flippant, experiential, extroverted**. Its strict negative traits are **solemn, formal, serious, introverted, perfectionist, meticulous, serene, conscientious, ritualistic, earnest, stoic, pensive, erudite, reverent, independent, principled**; the highly concentrated subset is **solemn, formal, serious, introverted, perfectionist, meticulous, serene, conscientious, ritualistic, earnest, independent, principled**.

The strongest broader associated traits, retained with exact correlations and all off-axis statistics in `qwen_pc2_crossmodel_evidence_packet.csv`, are:

| Local PC | Positive, strongest first | Negative, strongest first |
|---|---|---|
| Qwen PC2 | experiential, practical, casual, accessible, inquisitive, gregarious, humble, anxious, extroverted, adaptable | introverted, ritualistic, pensive, theoretical, abstract, reverent, conceptual, principled, solemn, erudite |
| LLaMA PC1 | grounded, contemporary, accessible, practical, transparent, secular, reductionist, experiential, humble, quantitative | ethereal, cryptic, bombastic, grandiose, poetic, spiritual, mystical, theatrical, enigmatic, dramatic |
| Gemma PC2 | casual, anxious, impatient, irreverent, flippant, experiential, nonchalant, extroverted, reactive, neurotic | solemn, formal, serious, introverted, perfectionist, meticulous, serene, conscientious, ritualistic, earnest |

Representative strength/off-axis rows show why specificity is distinct from raw correlation:

| Model-local PC | Trait | Target r | Largest off-axis r | Margin | Purity |
|---|---|---:|---:|---:|---:|
| Qwen PC2 | experiential | +.942 | PC6 -.152 | .790 | .946 |
| Qwen PC2 | introverted | -.954 | PC6 +.149 | .805 | .937 |
| LLaMA PC1 | grounded | +.937 | PC5 -.157 | .780 | .917 |
| LLaMA PC1 | ethereal | -.965 | PC2 +.214 | .751 | .941 |
| Gemma PC2 | casual | +.912 | PC3 -.275 | .637 | .868 |
| Gemma PC2 | solemn | -.954 | PC3 +.112 | .842 | .975 |

After keeping the observed positive orientations, the associated layer has three positive traits in all three models (**accessible, experiential, practical**) and 13 negative traits in all three (**abstract, ascetic, conceptual, erudite, introverted, meditative, pedantic, pensive, reverent, ritualistic, serene, specialized, theoretical**). Strict recurrence is sparser: Qwen/LLaMA share positive **practical** and negative **abstract, conceptual, theoretical**; Qwen/Gemma share positive **experiential** and negative **erudite, introverted, pensive, principled, reverent, ritualistic, solemn**. No focal strict marker occurs in all three, and LLaMA/Gemma share no focal strict marker despite substantial associated-layer recurrence.

Strict markers unique to one focal local PC are:

- Qwen positive: **inquisitive**; no Qwen strict negative marker is unique relative to both other models.
- LLaMA positive: **accessible, contemporary, grounded**. LLaMA negative: **artistic, ascetic, bombastic, chaotic, creative, cryptic, deterministic, dramatic, eclectic, enigmatic, epicurean, esoteric, ethereal, fatalistic, grandiose, historical, idealistic, innovative, meditative, melodramatic, metaphorical, mystical, paradoxical, philosophical, poetic, rhetorical, romantic, spiritual, theatrical, whimsical**.
- Gemma positive: **anxious, casual, extroverted, flippant, impatient, irreverent, nonchalant, reactive**. Gemma negative: **conscientious, earnest, formal, independent, meticulous, perfectionist, serene, serious, stoic**.

### Interpretation

LLaMA PC1 does provide a cleaner *within-model* concrete/accessible versus symbolic/abstract contrast than Qwen PC2’s small positive strict set, but it does **not** provide a cleaner isolated decomposition of the Qwen-PC2-corresponding direction. Its negative pole is dominated by poetic, mystical, theatrical, rhetorical, and creative markers that are canonical Qwen-PC1-negative content. This is exactly the pattern expected if LLaMA PC1/PC2 rotate and redistribute the Qwen PC1/PC2 plane.

Gemma PC2 more directly corroborates Qwen PC2. Its positive pole preserves experience and adds immediacy, outwardness, reactivity, and informality; its negative pole preserves inwardness, ritual, reverence, principle, solemnity, and erudition while adding seriousness, formality, meticulousness, and self-control. Gemma is therefore stronger evidence for the bipolar organization than LLaMA PC1 alone.

Across models, the AA-8 wording is strengthened at the broad descriptive level but should be narrowed. The most stable common contrast is **immediate, outward, accessible engagement versus inward, abstract, solemn/formally mediated reflection**. “Practical” is not strict in Gemma, “experiential” is not strict in LLaMA, and “integration” is not directly named by the strict recurring traits, so a universal **direct experiential versus integrated abstraction** label would overstate the evidence.

### Hypothesis

The three aligned model-local directions may instantiate a recurring engagement-versus-mediation organization, while each PCA basis allocates nearby expressive-symbolic, reactive-social, and standards/formality variance differently. This is a hypothesis about recurring organization, not a claim of shared latent homology.

### Unknown

It remains unknown whether the focal PCs share a causal latent variable, whether their semantic differences reflect architecture/training or PCA rotation, and whether the trait names measure validated constructs. Score correspondence and same-space trait recurrence cannot decide those questions.

## Secondary marker-comparison packets

### Qwen PC1 / LLaMA PC1-PC2 subspace / Gemma PC1

**Observed:** Qwen PC1 and Gemma PC1 have 60 and 65 strict markers and closely recur on empirical/procedural positive versus imaginative-symbolic negative content. LLaMA PC1 contributes much of the imaginative-symbolic negative family, while sign-reversed LLaMA PC2 contributes a large standards/care/structure versus reactive/disorganized contrast. The exact rows are in `crossmodel_marker_comparison.csv`.

**Interpretation:** the LLaMA evidence belongs to a two-component PC1/PC2 subspace packet. Forcing LLaMA PC2 alone as “the PC1 equivalent,” or LLaMA PC1 alone as “the PC2 equivalent,” discards the observed redistribution.

### Qwen PC3 / LLaMA PC4 / Gemma PC3

**Observed:** role-score correspondence is strong (`+.802`, `+.806`), yet Qwen has 15 strict markers, LLaMA PC4 has none, and Gemma PC3 has only **challenging** on its positive pole.

**Interpretation:** the corresponding score direction is not expressed as an equally pure single-trait family in the other models. High score correlation alone is not PC specificity.

### Qwen PC4 / LLaMA PC3 / Gemma PC4

**Observed:** Qwen PC4 has no strict markers. LLaMA PC3 has strict positive **data_driven** and strict negative **empathetic, existentialist**. After reversing Gemma PC4 to Qwen orientation, Gemma’s sole strict marker is **literal** on the Qwen-positive pole.

**Interpretation:** these sparse, nonrecurring markers do not support a shared semantic label.

### Qwen PC5 / LLaMA PC5 / Gemma PC5

**Observed:** none of the three aligned local PCs has a strict marker, despite score correlations of `+.688` and `-.651`.

**Interpretation:** the result preserves a recurring role-score direction while withholding trait-specific interpretation.

## Scientific boundaries

### Observed

- Saved 275-role by 240-trait matrices, saved model-local PC scores, exact frozen-rule memberships, explained variance, and canonical role-score correlations.
- Qwen reproduction and all verification checks pass.

### Interpretation

- Trait families are descriptive same-space activation-vector overlays; trait names are not validated latent constructs.
- Cross-model correspondence can motivate comparison but cannot establish component identity.

### Hypothesis

- Recurring oriented trait families may reflect a shared organization of role-conditioned model states.

### Unknown

- Latent homology, causal mechanism, behavioral realization, and any human/model equivalence.

No human respondent was loaded, scored, imputed, or projected. No PCA was recomputed. No model inference, activation extraction, response generation, external model API, GPU, or RunPod was used. Claims 14 and 15 are not changed: the result adds bounded cross-model evidence and a rotation caveat without altering their Qwen-focused wording. Sticky notes: no changes.
