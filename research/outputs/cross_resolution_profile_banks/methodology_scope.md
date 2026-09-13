# AA-12 cross-resolution profile banks: methodology and scope

Status: **ACTIVE, HUMAN-ONLY AND MODEL-ONLY BANK CONSTRUCTION; CROSS-DOMAIN MATCHING PROHIBITED**

Date: 2026-09-13

Thread: existing AA-12 conversation, follow-up 2

Track: Track 1 — independent profile-group correspondence (ACTIVE)

This phase materializes two independent, resolution-indexed inputs for a later preregistered correspondence analysis:

1. the already-frozen SAPA partial-response latent-class solutions at K=4 through K=10; and
2. new, independently fitted Qwen, LLaMA, and Gemma role-vector partitions at K=4 through K=10.

It does not calculate a human/model similarity, assignment, correspondence score, shared representation, or preferred cross-domain K pair. Equal K is not assumed. The intended later design may compare any human K in 4–10 with any model K in 4–10, but that design and its null tests are outside this phase.

The human bank reuses the exact method frozen in AA-12 commit `6b2e460f19efca5d4dbb47487461790651d34208` and preserves the previously frozen eligibility judgments. No likelihood, pseudocount, split, seed, start count, stopping rule, response treatment, missingness treatment, class-size rule, or alignment rule is retuned. A fitted but previously ineligible K remains explicitly diagnostic/ineligible.

The model bank uses the separately frozen method in `model/model_clustering_prefit_freeze.md`. Human responses, profiles, item wording, and eligibility evidence are not inputs to model clustering. Model role names and the 240 trait labels may be used only after the anonymous numerical partitions have been committed.

Human respondent rows, masks, IDs, posterior memberships, and imputed values remain private and uncommitted. Model role membership is non-human aggregate/design-inventory data and may be published after the numerical freeze. No new inference, prompt generation, activation extraction, external model API, GPU, or RunPod work is authorized.
