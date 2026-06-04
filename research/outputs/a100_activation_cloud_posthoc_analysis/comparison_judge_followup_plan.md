# Comparison Judge Follow-Up Plan

Do not rerun generation or activation extraction. Use the saved `judge_input_responses.jsonl` and `activation_cloud_per_response.csv`.

1. Score the same 120 responses with the comparison judge using the same role-expression rubric and no activation coordinates.
2. Compare retained-response overlap for score>=2 and score==3 by role using Jaccard overlap and disagreement counts.
3. Recompute centroid shifts, variance shifts, covariance eigenvectors, and outlier sets under each judge.
4. Inspect disagreements where one judge retains and the other rejects, especially near-centroid rejects and far-centroid retained responses.
5. Treat stable retained subsets across judges as higher-confidence role-expression clouds; treat judge-sensitive shifts as evaluator-model sensitivity.
