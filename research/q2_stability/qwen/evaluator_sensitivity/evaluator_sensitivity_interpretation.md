# Evaluator Sensitivity Interpretation

The evaluator-sensitivity comparison is blocked, not completed. The local script imported 192 existing Codex GPT-5.5 Standard scores across trickster and editor, but the attempted `gpt-4.1-mini` canonical-rubric rescore failed with OpenAI `insufficient_quota`, leaving zero paired evaluator records.

Current usable state: the harness, canonical prompt path, response-corpus mapping, Codex-side baseline, summary schema, and confusion-matrix outputs are prepared. Next step is to rerun `python3 research/q2_stability/qwen/scripts/evaluator_sensitivity_analysis.py` after API quota is restored. Until then, no conclusion should be drawn about evaluator sensitivity or whether judge substitution contributed to editor extraction failure.
