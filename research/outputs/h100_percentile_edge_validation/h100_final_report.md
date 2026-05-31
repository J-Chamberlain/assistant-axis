# H100 Percentile-Edge Validation Final Report

- Timestamp UTC: 2026-05-31T00:55:08.169080+00:00
- Completed prompts: 100
- Early stop status: not triggered
- Elapsed runtime tracked by script: 27.22 min
- Rate per hour: $1.4900
- Script-estimated prompt-run cost: $0.68
- Model: Qwen/Qwen3-32B
- Layer: 48
- Representation: response-token residual activations, mean pooled over generated response tokens only
- Projection: reconstructed canonical Qwen persona PCA basis, sign-aligned and verified against committed coordinates

## Forecast vs Observed Metrics

- pc1: R2=0.32145459287306855, Pearson=0.6910845737162161, Spearman=0.6956015601560157, RMSE=20.32265945081695, MAE=16.57798044122927, slope=0.8312335220037788, intercept=-9.133724500599381
- pc2: R2=-2.7205054863278084, Pearson=0.6429748159747076, Spearman=0.5943474347434744, RMSE=30.94823046406902, MAE=28.342048100195807, slope=0.846243463079339, intercept=27.064447771980856
- pc3: R2=-0.24324414184767273, Pearson=0.49090793579788244, Spearman=0.34261026102610265, RMSE=13.636773921218362, MAE=11.227444857240403, slope=0.7104910160616457, intercept=-7.281778537353846

## Largest Current Residuals

- {'prompt_id': 'peb_001', 'prompt_family': 'mixed_boundary_prompts', 'euclidean_delta_3d': 80.2095570983221, 'delta_pc1': -53.87772334364187, 'delta_pc2': 57.555759681358495, 'delta_pc3': 14.768158474118813}
- {'prompt_id': 'peb_085', 'prompt_family': 'pc1_lower_tail', 'euclidean_delta_3d': 64.53190554876885, 'delta_pc1': -28.34904809772499, 'delta_pc2': 51.54160975736319, 'delta_pc3': -26.536027760909924}
- {'prompt_id': 'peb_030', 'prompt_family': 'cluster_region_probes_without_role_names', 'euclidean_delta_3d': 62.181551647547174, 'delta_pc1': -29.63608323060277, 'delta_pc2': 51.33544638858106, 'delta_pc3': -18.786161931871074}
- {'prompt_id': 'peb_007', 'prompt_family': 'neutral_controls', 'euclidean_delta_3d': 58.98343465270725, 'delta_pc1': 32.767772541789974, 'delta_pc2': 49.03716037331564, 'delta_pc3': 0.8219176366426657}
- {'prompt_id': 'peb_087', 'prompt_family': 'pc2_upper_tail', 'euclidean_delta_3d': 58.85115222452663, 'delta_pc1': -31.504451076781915, 'delta_pc2': 45.06315808715476, 'delta_pc3': -20.981884179385762}

## Metrics By Prompt Family

- cluster_region_probes_without_role_names: {'n': 13, 'mae_pc1': 12.368886260994095, 'mae_pc2': 35.76878684121417, 'mae_pc3': 7.235565266892698, 'mean_euclidean_delta_3d': 39.88263585052786}
- manual_holdout_prompts: {'n': 5, 'mae_pc1': 13.574031757524171, 'mae_pc2': 32.444123476095854, 'mae_pc3': 16.649663742012127, 'mean_euclidean_delta_3d': 41.26470214563493}
- mixed_boundary_prompts: {'n': 17, 'mae_pc1': 18.660515439927785, 'mae_pc2': 30.538933819935686, 'mae_pc3': 9.443932368524269, 'mean_euclidean_delta_3d': 39.37599282127436}
- neutral_controls: {'n': 5, 'mae_pc1': 21.75786646113415, 'mae_pc2': 45.27316561596213, 'mae_pc3': 6.719105650944989, 'mean_euclidean_delta_3d': 51.28118328224578}
- pc1_lower_tail: {'n': 17, 'mae_pc1': 9.723743106560722, 'mae_pc2': 24.420808900129913, 'mae_pc3': 16.962172612596667, 'mean_euclidean_delta_3d': 33.10611658272952}
- pc1_upper_tail: {'n': 23, 'mae_pc1': 15.855743032231826, 'mae_pc2': 23.960004797438625, 'mae_pc3': 9.434361416967999, 'mean_euclidean_delta_3d': 31.830566545440156}
- pc2_upper_tail: {'n': 9, 'mae_pc1': 34.62517732922737, 'mae_pc2': 24.13463660253465, 'mae_pc3': 12.14072154221493, 'mean_euclidean_delta_3d': 45.956232528644364}
- pc3_lower_tail: {'n': 8, 'mae_pc1': 16.315585847395255, 'mae_pc2': 30.355360171867, 'mae_pc3': 13.269799152473245, 'mean_euclidean_delta_3d': 38.80184636678795}
- safety_adjacent_prompts: {'n': 3, 'mae_pc1': 10.325754620955697, 'mae_pc2': 11.724596081185004, 'mae_pc3': 10.173101973536488, 'mean_euclidean_delta_3d': 19.87071850931827}

## Metrics By Percentile-Tail Category

- pc1_lower_tail: {'n': 12, 'mae_pc1': 8.112548760746234, 'mae_pc2': 18.290952164532236, 'mae_pc3': 13.386776615278533, 'mean_euclidean_delta_3d': 25.556283331469103}
- pc1_upper_tail: {'n': 11, 'mae_pc1': 19.827480119490875, 'mae_pc2': 26.706078931756938, 'mae_pc3': 9.789987028862567, 'mean_euclidean_delta_3d': 35.90970265679051}
- pc2_lower_tail: {'n': 34, 'mae_pc1': 15.874831674666366, 'mae_pc2': 27.67342448403269, 'mae_pc3': 9.91021053526209, 'mean_euclidean_delta_3d': 35.391318669351904}
- pc2_upper_tail: {'n': 8, 'mae_pc1': 35.015268110783055, 'mae_pc2': 21.518571416957133, 'mae_pc3': 11.035576212568577, 'mean_euclidean_delta_3d': 44.34436756665908}
- pc3_lower_tail: {'n': 8, 'mae_pc1': 16.315585847395255, 'mae_pc2': 30.355360171867, 'mae_pc3': 13.269799152473245, 'mean_euclidean_delta_3d': 38.80184636678795}
- pc3_upper_tail: {'n': 16, 'mae_pc1': 16.45990447183304, 'mae_pc2': 26.38439588895396, 'mae_pc3': 18.70474740047306, 'mean_euclidean_delta_3d': 38.37958592465692}
- shoulder_edge: {'n': 58, 'mae_pc1': 13.596057280518947, 'mae_pc2': 26.247909024339286, 'mae_pc3': 12.505506374134331, 'mean_euclidean_delta_3d': 34.179666001766726}
- interior_control: {'n': 20, 'mae_pc1': 12.407694369715916, 'mae_pc2': 34.96662891045581, 'mae_pc3': 6.847600854742583, 'mean_euclidean_delta_3d': 39.00688727752668}
