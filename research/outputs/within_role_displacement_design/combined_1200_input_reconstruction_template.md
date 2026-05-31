# Combined 1,200 Input Reconstruction Template

- Generated UTC: 2026-05-31T16:16:54.254880+00:00
- model_used: GPT-5.5
- No GPU used.

Once `target_role` is selected, reconstruct one row for every positive-instruction and extraction-question pair:

```text
for each instruction_id in 0..4:
  system_message = role_positive_instruction[target_role][instruction_id]
  for each question_id in 0..239:
    user_message = extraction_questions[question_id]
```

Recommended output columns:

```csv
target_role,instruction_id,question_id,system_message,user_message,target_role_pc1,target_role_pc2,target_role_pc3,instruction_predicted_delta_pc1,instruction_predicted_delta_pc2,instruction_predicted_delta_pc3,question_predicted_delta_pc1,question_predicted_delta_pc2,question_predicted_delta_pc3,additive_predicted_delta_pc1,additive_predicted_delta_pc2,additive_predicted_delta_pc3,expected_role_expression_effect,instruction_rationale,question_rationale
```

Important constraints:

- The target is displacement around the selected role centroid, not absolute global PCA position.
- Do not assume the selected role centroid is the origin.
- Exact token-level rendering should be produced with the same tokenizer/chat-template conventions as the later corrected extraction run.
- Public artifacts do not include original successful-response masks, so any retained-response analysis requires fresh role-expression scoring.
