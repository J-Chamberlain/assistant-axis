# AA-19 independent human test of five model-consensus axes

**Overall decision: 2. Partial human convergence.** Human factor fitting and selection used only the verified SAPA item responses, frozen scoring, and future-safe unique direct human proxy correlations. AA-18 loadings entered only after the human solution was frozen. No HiFWB value or association entered any estimate.

## Phase gate and model bridge

**Observed:** The 23,679-row SAPA release and official scoring keys match prior SHA256 fingerprints. The reconstructed 45-label aggregate proxy correlation matrix matches AA-1 within 5×10⁻⁹. The primary bridge has 41 unique-source future-safe direct proxies from 45 direct labels; 65 unique-source future-safe labels are available when close proxies are added. No complete respondent profiles were fabricated.

| Axis | Primary bridge consensus r | Lowest model r | Positive/negative mass | Bridge gate | Human class |
|---|---:|---:|---:|---|---|
| C1 | 0.984 | 0.969 | 0.172/0.195 | pass | C_human_combination |
| C2 | 0.896 | 0.866 | 0.156/0.159 | pass | B_partial_human_analogue |
| C3 | 0.936 | 0.860 | 0.204/0.166 | pass | A_independently_supported |
| C4 | 0.857 | 0.735 | 0.163/0.117 | fail | D_presently_untestable |
| C5 | 0.687 | 0.528 | 0.130/0.096 | fail | D_presently_untestable |

An inadequate bridge yields class D even if a restricted human alignment looks high. C4 is close to the direct-only model-score threshold (weakest r=0.735) and rises to 0.807 with future-safe close proxies; C5 rises from 0.528 to 0.750. Both remain D under the frozen primary direct-only rule. Direct-only, alias handling, close-proxy, and leave-one-trait-out results are separately exported.

## Independently estimated human structure

**Observed:** Parallel analysis retains 6 dimensions; Velicer MAP selects 6 within the tested 0–12 range; the held-out one-standard-error rule selects 5. The frozen combined rule fits **5 oblique minimum-residual human factors**. The human loading subspace is stable under respondent bootstrap and split halves. Individual factor stability is H1=stable, H2=stable, H3=stable, H4=stable, H5=stable. The criteria need not agree because planned missingness and proxy reuse change the effective information.

Post-freeze QA repeats the held-out selection with eight independent five-fold split sets: 5 factors in 7/8 sets, 6 factors in 1/8 sets. This estimates split sensitivity; it does not replace the predeclared seed or selection rule.

| Human factor | Strongest positive proxies | Strongest negative proxies |
|---|---|---|
| H1 | stoic, serene, calm | anxious, temperamental, emotional |
| H2 | bitter, manipulative, vindictive | agreeable, forgiving, empathetic |
| H3 | extroverted, gregarious, theatrical | reserved, pessimistic, cynical |
| H4 | creative, innovative, artistic | traditional, callous, vindictive |
| H5 | meticulous, perfectionist, conscientious | rebellious, secular, impulsive |

The five restricted AA-18 loading vectors and the retained human factor subspace have canonical correlations 0.920, 0.891, 0.809, 0.589, 0.218; minimum-axis mapping-null p=0.002. This subspace statistic does not identify one-to-one axes.

Spearman item-pair sensitivity reproduces the human proxy correlation pattern at upper-triangle r=0.997; the five-factor subspaces have minimum canonical correlation 0.998. This changes association estimator, not the planned administration design.

## Model–human comparison

**Observed:** Future-safe direct trait-covariance upper-triangle correlations with human proxies are Qwen 0.437 (p=0.002), Llama 0.611 (p=0.002), Gemma 0.455 (p=0.002), Consensus 0.531 (p=0.002).

| Axis | Human-subspace projection r | Best human factor | Best single Tucker | Mapping-null p | Classification |
|---|---:|---|---:|---:|---|
| C1 | 0.875 | H2 | 0.542 | 0.002 | C_human_combination |
| C2 | 0.794 | H1 | 0.590 | 0.002 | B_partial_human_analogue |
| C3 | 0.857 | H2 | 0.744 | 0.002 | A_independently_supported |
| C4 | 0.792 | H4 | 0.753 | 0.002 | D_presently_untestable |
| C5 | 0.596 | H3 | 0.530 | 0.002 | D_presently_untestable |

**Post-freeze factor-count sensitivity:** The six-factor solution was inspected because PA/MAP retain six and one of eight held-out split sets selects six. Projection and best-single-factor congruence under five versus six human factors are:

| Axis | 5-factor projection / single | 6-factor projection / single |
|---|---:|---:|
| C1 | 0.875 / 0.542 | 0.876 / 0.565 |
| C2 | 0.794 / 0.590 | 0.802 / 0.521 |
| C3 | 0.857 / 0.744 | 0.874 / 0.675 |
| C4 | 0.792 / 0.753 | 0.799 / 0.768 |
| C5 | 0.596 / 0.530 | 0.605 / 0.533 |

C3 meets class A under the frozen five-factor primary solution, but its best single-factor congruence falls below the 0.70 threshold under six factors (0.675). Its **human-subspace** correspondence remains high. Treat the individual human-axis match as factor-count sensitive; a later HiFWB test should not rely on H2 as a uniquely resolved human counterpart.


**Interpretation:** The human factor subspace comparison asks whether the model loading pattern lies within independently estimated human trait covariance. It does not require a one-to-one axis match. A high model-side bridge reconstruction is a gate on testability, not human validation. Weak direct mapping coverage and shared item sources constrain every human analogy.

## Secondary Big Five context

Official IPIP100 keys were compared after factor fitting. Shared items can inflate these descriptive aggregate correlations. Neither Big Five keys nor model labels entered human factor retention or rotation.

| Human projection of model axis | Strongest official IPIP100 domain | Correlation | Big Five multiple R² |
|---|---|---:|---:|
| C1 | IPIP100stability | -0.479 | 0.698 |
| C2 | IPIP100consc | +0.479 | 0.546 |
| C3 | IPIP100agree | +0.814 | 0.723 |
| C4 | IPIP100intel | +0.692 | 0.613 |
| C5 | IPIP100extra | +0.695 | 0.669 |

These descriptive R² values do not establish novelty beyond the Big Five: source-item overlap and planned missingness require a later independent test. The strongest C3 relationship is with Agreeableness, but the model axis is not defined by that domain.

## Limits and next gate

**Observed:** SAPA planned missingness provides group-level pairwise proxy correlations, with far fewer co-observations per proxy pair than 23,679. The Gaussian parallel reference approximates effective N but does not preserve the empirical item marginals or joint missingness mask; the held-out and MAP disagreement is retained. The semantic bridge is provisional and lacks independent expert adjudication. The model vectors share prompts/labels and retain the AA-15 historical extraction limitation. No human respondent was projected into model activation space.

**Interpretation:** Proceed to a separate HiFWB analysis only for axes with adequate future-safe bridge coverage and reproducible human alignment, with an independent outcome freeze and duplicate-aware sensitivity. Class D axes require better human proxies before any wellbeing test. This package establishes neither causal traits nor model–human psychological equivalence.

**Hypothesis:** Training data, instruction or preference tuning, common prompts, and bridge semantic limitations may each explain convergence or divergence. This analysis cannot distinguish those causes.

No model inference, RunPod, paid compute, HiFWB fitting, persona wellbeing scoring, viewer deployment, or respondent-level export occurred.
