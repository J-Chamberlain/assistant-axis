# Existing activation sample audit
Audit date: 2026-09-24. Scope: existing artifacts, public metadata and small CPU checks only. Analyst: GPT-6 Astra. No model generation, inference, extraction, new judging, GPU, human structural comparison, data migration or push.

## Plain answers

| Model | Original-study personas with recoverable response distributions | Original-study traits with recoverable polarity distributions | Later local named-persona distributions | Third-party release |
|---|---:|---:|---|---|
| Qwen/Qwen3-32B | 0/275 | 0/240 | 4/275 personas, 6 role/run pairs: 2 personas retain full feature vectors at one layer; all 4 have projected clouds | 20 personas with keyed activation headers, across 3 separate runs, plus 3 default runs; payload and extraction compatibility unverified |
| meta-llama/Llama-3.3-70B-Instruct | 0/275 | 0/240 | 0 found | none in inspected releases |
| google/gemma-2-27b-it | 0/275 | 0/240 | 0 found | none in inspected releases |

All 275 persona and 240 trait aggregate vectors survive for each model: 1,545 files, all byte hashes matching the pinned Lu release. **Zero recovered original distributions is an availability result, not zero variability.** It does not establish absence from private archives. The inventory explicitly lists every model × persona/trait aggregate and every missing original sample set. Counts refer to these extraction samples, not steered dialogue turns or arbitrary nearest-persona assignments.

**Gregariousness:** its definition, paired instructions, questions, rubric and three aggregate contrast tensors survive. Neither polarity's original response activations/text, judge scores, retained membership, sample pairing nor exact aggregation weights was found for any model. Its positive-minus-negative mean vector cannot be reconstructed or bootstrapped. No reconstruction was attempted without inputs.

**Analyse now:** local projected width/orientation, grouped centroid uncertainty, prompt/question and existing-filter sensitivity; fixed-vector Qwen gregariousness readouts for trickster/editor full-feature responses using the matching released layer row. These would be model geometric scores, not human IPIP scores. Only the audit checks were run.

**Blocked:** original response-level coverage in every model; gregariousness polarity separation and estimated-direction uncertainty; all-layer response averages for the local single-layer runs; full-feature reanalysis of amateur/playwright. Third-party metadata offers a separate recovery lead, not original-study recovery.

**Smallest useful next analysis:** a separately authorized CPU-only, prompt/question-grouped sensitivity analysis of fixed layer-48 gregariousness cosine scores in the existing raw trickster (1,200) and editor (128 and 64, separate) runs, with all-response and existing-judge filters. It would test the utility of a conditional readout before expanding scope, not repair AA27 or begin a human comparison.

## Evidence and limits

All 1,545 local release hashes match revision `3b3b788432ad33e3a28d9ff08e88a530c0740814`; released rows are layers, not samples. The five main Qwen clouds contain 1,512 distinct run-qualified IDs, with exact source/viewer coordinate agreement. The older 104-response normalized trickster run is separate. Existing role-expression scores were inventoried, not rerun, and are not gregariousness scores.

[Detailed methods and source findings](methods.md) cover the AA15 layer-mean correction, AA27's unchanged failed gate, public-release pins, gregarious prompt/rubric content, filtering, projection limits and grouped resampling. [Inventory](inventory.csv), [source manifest](source_manifest.json), [checks](validation_summary.json), [search boundary](search_log.json) and [successor handoff](HANDOFF.md) accompany this report. No human comparison or follow-on analysis was begun.
