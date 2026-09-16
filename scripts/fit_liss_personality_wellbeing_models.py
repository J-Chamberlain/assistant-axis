#!/usr/bin/env python3
from liss_common import *

require_files(*EXPECTED_FILES, BIG_FIVE_KEY)
try:
    import numpy as np
    import pandas as pd
    from sklearn.compose import TransformedTargetRegressor
    from sklearn.decomposition import PCA
    from sklearn.impute import SimpleImputer
    from sklearn.kernel_ridge import KernelRidge
    from sklearn.linear_model import LinearRegression, RidgeCV
    from sklearn.metrics import r2_score, mean_squared_error
    from sklearn.model_selection import KFold, cross_validate, GridSearchCV
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    raise SystemExit(f"scientific Python dependencies are required after data arrival: {exc}")

joined = load_joined()
x = score_big_five(joined)
y = score_hifwb(joined)
contents = [c for c in y if not c.endswith("__valid_items") and c not in {"questionnaire_version", "timeframe"}]
analysis = x.join(y[contents], how="inner")
cv = KFold(n_splits=5, shuffle=True, random_state=SEED)
models = {
    "P0_bigfive_linear": make_pipeline(SimpleImputer(), StandardScaler(), LinearRegression()),
    "P1_predictor_covariance_pc1": make_pipeline(SimpleImputer(), StandardScaler(), PCA(n_components=1), LinearRegression()),
    "P2_full_5d_ridge": make_pipeline(SimpleImputer(), StandardScaler(), RidgeCV(alphas=np.logspace(-4, 4, 33))),
    "P3_rbf_kernel_ridge_sensitivity": GridSearchCV(
        make_pipeline(SimpleImputer(), StandardScaler(), KernelRidge(kernel="rbf")),
        {"kernelridge__alpha": [0.1, 1.0, 10.0], "kernelridge__gamma": [0.01, 0.1, 1.0]}, cv=3),
}
results = []
for outcome in contents:
    usable = analysis[x.columns.tolist() + [outcome]].dropna(subset=[outcome])
    for name, model in models.items():
        fitted = TransformedTargetRegressor(regressor=model, transformer=StandardScaler())
        scores = cross_validate(fitted, usable[x.columns], usable[outcome], cv=cv,
                                scoring={"r2": "r2", "mae": "neg_mean_absolute_error"}, n_jobs=1)
        results.append({"outcome": outcome, "model": name, "n": len(usable),
                        "heldout_r2_mean": float(np.mean(scores["test_r2"])), "heldout_r2_sd": float(np.std(scores["test_r2"])),
                        "heldout_mae_mean": float(-np.mean(scores["test_mae"]))})
payload = {"status": "complete", "seed": SEED, "geometry_defined_from": "Big Five predictors only within training folds",
           "results": results, "respondent_rows_written": False, "environment": environment_record()}
write_local_json("personality_wellbeing_model_summary.json", payload)
print(json.dumps(payload, indent=2))
