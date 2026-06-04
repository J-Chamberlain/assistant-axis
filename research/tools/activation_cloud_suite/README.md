# Activation Cloud Suite

Reusable no-GPU analysis scaffold for future persona activation-cloud pilots.

Inputs: `activation_cloud_per_response.csv`, `judge_input_responses.jsonl`, optional judge score CSVs, and `geometry_viz_data.json`.

Typical usage:

```bash
python research/tools/activation_cloud_suite/run_activation_cloud_suite.py --config research/tools/activation_cloud_suite/config_template.json
```

The suite pattern runs cloud shape statistics, covariance/eigendecomposition, bootstrap centroid convergence, optional OpenAI judge scoring, judge-filtered summaries, judge-model comparison, standalone visualization generation, and a report-ready conclusion. It does not require GPU and must not alter original pilot outputs.
