# Prior grouping audit

Source: `research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py` (`GROUPS`), reused by `research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py`. Five groups contain three equal-weight trait labels each (15 of 240). The source comment says they were chosen from descriptions, not fitted to PC correlations. They are manual/editorial semantic selections, shared verbatim across Qwen, Llama, and Gemma. The viewer averages within-model percentile profiles. Membership is one group per selected trait; the other 225 traits are ungrouped. The grouping uses trait descriptions/names, then persona-profile percentiles for display, not factor estimation or activation clustering. It is an external comparison only.

| Editorial group | Members | AA-17 primary factors (Qwen / Llama / Gemma) |
|---|---|---|
| Exploration | creative, abstract, curious | Qwen_F3, Qwen_F1, Qwen_F4 / Llama_F2, Llama_F4, Llama_F6 / Gemma_F6, Gemma_F6, Gemma_F4 |
| Response | reactive, adaptable, practical | Qwen_F3, Qwen_F3, Qwen_F1 / Llama_F6, Llama_F2, Llama_F6 / Gemma_F6, Gemma_F6, Gemma_F2 |
| Scrutiny | skeptical, analytical, conscientious | Qwen_F3, Qwen_F1, Qwen_F2 / Llama_F3, Llama_F6, Llama_F3 / Gemma_F6, Gemma_F1, Gemma_F2 |
| Challenge | rebellious, competitive, manipulative | Qwen_F1, Qwen_F1, Qwen_F1 / Llama_F1, Llama_F1, Llama_F4 / Gemma_F3, Gemma_F3, Gemma_F3 |
| Affiliation | empathetic, agreeable, altruistic | Qwen_F1, Qwen_F1, Qwen_F2 / Llama_F1, Llama_F1, Llama_F3 / Gemma_F3, Gemma_F3, Gemma_F5 |

Within-triplet agreement in primary assignment:
- Exploration: Qwen 3/3 distinct factors; Llama 3/3 distinct factors; Gemma 2/3 distinct factors
- Response: Qwen 2/3 distinct factors; Llama 2/3 distinct factors; Gemma 2/3 distinct factors
- Scrutiny: Qwen 3/3 distinct factors; Llama 2/3 distinct factors; Gemma 3/3 distinct factors
- Challenge: Qwen 1/3 distinct factors; Llama 2/3 distinct factors; Gemma 1/3 distinct factors
- Affiliation: Qwen 2/3 distinct factors; Llama 2/3 distinct factors; Gemma 2/3 distinct factors
