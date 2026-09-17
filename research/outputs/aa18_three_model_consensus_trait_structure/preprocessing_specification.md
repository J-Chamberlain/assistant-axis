# Preprocessing specification

Primary: within each model and each training fold, subtract the training-persona mean and divide by training-persona sample SD for each of 240 signed trait columns. Apply these frozen parameters to held-out personas. No label-based sign reversal. The full-data standardization is used only for descriptive direct convergence, full-sample scores, and post-fit visualization. Model-specific SVD, ridge projection, and score scaling are refit inside each training fold. Raw cosine metrics are separately exported.
