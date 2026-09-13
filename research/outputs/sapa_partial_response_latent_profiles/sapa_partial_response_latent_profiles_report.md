# SAPA partial-response latent profile discovery

Status: **complete human-only analysis; conflicted K=4/K=10 numerical anchors; no unique profile count selected**

Pre-fit freeze commit: `6b2e460f19efca5d4dbb47487461790651d34208`
Numerical/profile freeze commit: `f0e55723eacc16730d4d9184bcb8bb9868458fb0`

## Executive result

A categorical latent-class model can extract recurring response configurations directly from SAPA's overlapping partial responses, without filling a single missing cell. The evidence does not support one clearly preferred or highly stable class count.

The frozen selection criteria conflict. Validation predictive likelihood favors eligible K=10, while BIC and ICL favor K=4. Their formal support sets do not intersect, so the preregistered fallback retains **K=4 and K=10 as separate evidential anchors**, not as a contiguous neighboring range. The K=4 configuration has moderate independent split-refit stability (mean aligned distance 0.091721); K=10 has low stability (0.153987). Response-style summaries predict both solutions above chance and trigger the preregistered warning, especially at K=4. Administration masks do not.

The defensible conclusion is therefore bounded: **broad human response-profile structure is recoverable, but neither a unique K nor a stable fine-grained taxonomy is established; response style remains a material interpretive warning.**

## Data and integrity

Source: Harvard Dataverse SAPA V5, DOI `10.7910/DVN/SD7SVE`, artifact `sapaTempData696items08dec2013thru26jul2014.tab`.

- Respondents: 23,679.
- Respondent-matrix columns: 719.
- Canonical behavioral items expected and present: 696 of 696, identified from the committed canonical item dictionary.
- Excluded fields: RID plus 22 demographic, occupation, and derived fields.
- Observed response codes: integers 1–6 only.
- Missing responses: empty TAB cells; excluded from likelihood and sufficient statistics.
- Observed behavioral cells: 2,039,803 (12.377%); median 71 answered items, range 0–311.
- Duplicate or missing RIDs: 0; RID was used for integrity checking only and discarded.
- One respondent had no behavioral response. This row did not enter fitting or per-answer prediction and received the class-prior posterior for aggregate certainty accounting.
- Administration: the source's planned random-subset design was retained exactly; masks were not regularized or completed.

No respondent-level response, mask, split, class assignment, posterior, inferred answer, or imputed profile is committed.

## Frozen method

The primary model is a conditionally independent product-multinomial finite mixture. Each class has a six-category probability distribution for every one of 696 items. For respondent `i`, only actually observed items `j in O_i` enter:

`P(x_i observed) = sum_k pi_k * product_{j in O_i} theta[k,j,x_ij]`.

The ordered response labels remain 1–6 in reporting, but the categorical likelihood does not impose equal spacing. Batch EM uses a sparse respondent × item-category indicator matrix, symmetric category pseudocount 0.5, six deterministic starts per K, fixed seeds, and the fully specified convergence and tie rules in `prefit_decision_record.md`.

Respondents with at least one answer were deterministically split into 14,206 discovery, 4,735 validation, and 4,737 locked replication rows. Missingness patterns were unchanged. Candidate K was frozen at 2–12, with a mechanical extension rule through at most 16. K=12 failed eligibility, so the rule stopped without fitting K=13.

This model's conditional-independence assumption is strong for personality data. The fitted classes are anonymous response-distribution summaries, not proof of natural psychological types.

## Synthetic implementation validation

The implementation passed the preregistered gate on 4,000 simulated respondents, 120 six-category items, four known classes, and 87.11% planned missingness. Six of six starts converged. Mean aligned profile distance was 0.06694, adjusted Rand index 0.87869, and aligned MAP accuracy 0.953. Changing every stored value under the missing mask changed neither likelihood nor posterior (maximum effect 0), and explicit label permutation was recovered exactly. Certainty increased with answered-item count.

## Model-selection evidence

| K | Eligible | Converged starts | Validation LL/answer | Replication LL/answer | BIC | ICL | Start distance |
|---:|:---:|---:|---:|---:|---:|---:|---:|
| 2 | yes | 6/6 | -1.569846 | -1.570047 | 3,899,319 | 3,900,829 | 0.000006 |
| 4 | yes | 4/6 | -1.537866 | -1.538361 | **3,866,990** | **3,869,618** | 0.000102 |
| 5 | yes | 5/6 | -1.530852 | -1.531814 | 3,875,610 | 3,878,550 | 0.032389 |
| 6 | yes | 4/6 | -1.526170 | -1.526968 | 3,887,847 | 3,890,956 | 0.029576 |
| 7 | yes | 4/6 | -1.522783 | -1.523773 | 3,903,750 | 3,906,688 | 0.084776 |
| 8 | yes | 4/6 | -1.518926 | -1.520163 | 3,920,748 | 3,923,647 | 0.059747 |
| 10 | yes | 4/6 | **-1.516536** | **-1.516922** | 3,964,560 | 3,967,346 | 0.092624 |
| 12 | no | 3/6 | -1.514157 | -1.515849 | 4,009,930 | 4,012,418 | 0.117520 |

K=3, 9, 11, and 12 were ineligible because fewer than four starts converged; K=12 also exceeded the 0.10 start-distance limit. AIC continued to improve through K=12, illustrating that different criteria answer different questions. Relative to K=4, K=10 improves mean log likelihood per observed answer by 0.02133 on validation and 0.02144 on locked replication, but pays a large parameter penalty and is less stable.

The frozen predictive one-standard-error set contains K=10. The frozen BIC/ICL support set contains K=4. The empty intersection prevents a unique winner.

## Frozen class sizes

Discovery MAP sizes and proportions are:

| Anchor | Anonymous profile sizes |
|---|---|
| K=4 | A 4,030 (28.4%); B 4,689 (33.0%); C 3,304 (23.3%); D 2,183 (15.4%) |
| K=10 | A 1,180 (8.3%); B 1,203 (8.5%); C 1,940 (13.7%); D 1,890 (13.3%); E 1,518 (10.7%); F 2,001 (14.1%); G 1,157 (8.1%); H 777 (5.5%); I 1,491 (10.5%); J 1,049 (7.4%) |

Every frozen discovery class exceeds the preregistered 2% effective and MAP minimum.

## Independent refit stability

- **K=4: moderate stability.** Mean weighted Jensen–Shannon profile distance is 0.091721; per-profile distances range 0.077267–0.108755.
- **K=10: low stability.** Mean distance is 0.153987; per-profile distances range 0.115298–0.215661. Only two of six replication starts met the strict convergence rule.

Broad four-profile organization reappears imperfectly. A specific ten-profile partition does not reproduce well enough to call stable.

## Posterior assignment certainty

Posterior probabilities use only each respondent's observed answers. No minimum-answer rule was selected.

| Anchor/subset | Median max posterior | Share >=0.70 | Share >=0.80 | Share >=0.90 |
|---|---:|---:|---:|---:|
| K=4, all rows | 0.999859 | 94.7% | 91.7% | 86.7% |
| K=4, validation | 0.999755 | 93.1% | 89.2% | 83.5% |
| K=4, replication | 0.999733 | 92.7% | 89.3% | 83.6% |
| K=10, all rows | 0.998199 | 93.0% | 89.4% | 83.5% |
| K=10, validation | 0.991240 | 86.9% | 80.3% | 72.4% |
| K=10, replication | 0.991566 | 86.9% | 81.0% | 72.1% |

Certainty rises with observed-item count for both anchors: Spearman rho is 0.3085 at K=4 and 0.3272 at K=10. At K=10, mean maximum posterior rises from 0.8446 in the lowest count bin (14–68 items) to 0.9867 in the highest (121–311). At K=4 the same relationship is positive but assignment is generally easier. The one zero-answer row has no response evidence and correctly receives only the largest prior probability (0.329 at K=4; 0.141 at K=10).

High numerical certainty should not be confused with correct ontology or model stability: a misspecified conditional-independence mixture can assign sharply.

## Administration-mask diagnostics

The full 696-item response mask does not predict frozen labels above chance on the independent replication subset:

| Anchor | Mask balanced accuracy | Chance | Count-only balanced accuracy | Max item-frequency range across profiles | Warning |
|---|---:|---:|---:|---:|:---:|
| K=4 | 0.2428 | 0.2500 | 0.2647 | 0.0337 | no |
| K=10 | 0.1024 | 0.1000 | 0.1080 | 0.0667 | no |

The result is therefore separable from simple item-administration classes under these diagnostics. This does not prove every aspect of missingness is irrelevant; it shows that the observed frozen labels are not recoverable from the administration mask alone.

## Response-style diagnostics

Raw response-style features include answered count, observed mean and variance, frequencies of categories 1 and 6, middle categories 3–4, extremes 1/6, high 5–6, low 1–2, and high-minus-low tendency.

| Anchor | Replication balanced accuracy | Chance | Item-pattern variance after generic level removal | Frozen warning |
|---|---:|---:|---:|:---:|
| K=4 | 0.6936 | 0.2500 | 99.0% | **yes** |
| K=10 | 0.4013 | 0.1000 | 96.5% | **yes** |

Both candidate anchors carry a material response-style warning. At K=10, for example, posterior-weighted extreme-category frequency ranges from about 8.2% in Profile D to 65.8% in Profile H; middle-category frequency ranges from 17.2% in H to 57.3% in D. This means the classes partly encode how respondents use the six-point scale.

The high item-pattern variance fractions provide an important counterpoint: subtracting generic profile-level elevation leaves almost all differentiated item structure. The safest reading is that response style is a strong correlate and likely contributor, not a complete account of the profiles.

## Anonymous signatures after numerical freeze

Wording was unblinded only after commit `f0e55723eacc16730d4d9184bcb8bb9868458fb0`. These summaries did not affect model selection.

The K=4 anchor separates: A, less reflective/idea-engaged and more deferential/quiet; B, socially comfortable and broadly upbeat; C, distressed, self-doubting, and socially uncomfortable; D, socially assertive, agentic, and task-forward.

The less-stable K=10 anchor separates: A, emotionally restrained/socially reserved; B, socially inhibited/background-oriented; C, rule-following/cautious/nondeceptive; D, comparatively less reflective/imaginative and less emotionally intense; E, energetic/socially confident/productive/positive; F, highly outgoing/party-oriented; G, distressed and low in self-regard; H, nervous/subdued and low in display-seeking; I, affectively labile/impulsive/impression-conscious; J, rule-breaking/risk/power-oriented/confrontational.

These are descriptions of item contrasts, not construct scores or established taxonomic labels. Full ranked evidence is in `semantic_profile_items.csv` and `semantic_profile_summary.md`.

## Answers to the primary questions

1. **Can stable recurring groups be recovered?** Broad structure is recoverable, but stability is only moderate at K=4 and low at K=10. A strongly stable discrete solution is not established.
2. **What K values are defensible?** The frozen evidence retains K=4 and K=10 as conflicted anchors. Eligible K=5–8 also fit validly but receive neither formal predictive-one-SE nor BIC/ICL support.
3. **One winner or neighboring range?** Neither. The evidence splits between two non-neighboring anchors; no unique winner is claimed.
4. **Stable across independent subsets?** Moderately for K=4, no for the fine-grained K=10 partition.
5. **Separable from administration artifacts?** Yes under mask-only and count-only diagnostics; neither triggers the warning.
6. **Separable from response style?** Not cleanly. Response style strongly predicts labels and triggers warnings, though most item-specific pattern variance remains after generic level removal.
7. **How confidently can respondents be assigned?** Aggregate posterior certainty is high, especially for K=4, but is lower out of sample for K=10 and does not rescue instability.
8. **How does confidence vary with answered items?** Positively and monotonically in aggregate; no threshold is selected.
9. **What are the anonymous signatures?** Full six-category item probability profiles for K=4 and K=10 are frozen and machine-readable; compact signatures are summarized above.
10. **What descriptions emerge after unblinding?** Broad social confidence/distress/agency/reflection configurations at K=4 and finer reserved, inhibited, conventional, energetic, outgoing, distressed, labile, and rule-breaking configurations at K=10, all subject to stability and response-style caveats.

## Boundaries

This task did not impute individual responses, score named constructs, run human PCA, perform clustering after imputation, load any model persona coordinates or model geometry, compare humans with Qwen/LLaMA/Gemma, run model inference, extract activations, use an external model API, use GPU/RunPod, or select a respondent/item threshold. External human-profile literature verification remains intentionally unperformed.

Track 1 remains ACTIVE. Tracks 2 and 3 remain PARKED. Human/model matching remains a later task.
