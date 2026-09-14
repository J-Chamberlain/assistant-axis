# SAPA Big Five Backbone — Demographic Stratification Sensitivity

Status: post-hoc structural robustness check requested by the user after the primary terrain design. This is not a preregistered population-reweighting analysis and must not be used to claim population representativeness.

The frozen Big Five scoring and full-sample standardization were retained. The density-backbone procedure was refit separately in eight large strata: female, male, age 24 or younger, age 25+, student, known nonstudent, USA, and non-USA. Each stratum exceeded N=3,000 except none; all therefore had ample sample size for the same kNN backbone procedure.

The broad central orientation recurs in every stratum. Coordinate-wise trajectory correlations with the full-sample backbone are generally high. USA and known-nonstudent curves are especially close to the full-sample curve, with median separations 0.180 and 0.198 standardized units. The largest median separation is 0.519 in the age-24-or-younger group. Density falloff away from the stratum-specific centerline is highly similar across groups, with robust slopes ranging from -0.422 to -0.465 and R2 from 0.791 to 0.836.

Age and student strata show more curvature than the full sample, while older, nonstudent, and USA strata are closer to the modestly curved full-sample centerline. This suggests demographic composition affects the exact centerline shape but does not explain away the broad high-density orientation or the strong falloff away from it.

These checks do not make the SAPA convenience sample representative. True population reweighting would require an external target population and defensible joint demographic margins. The present result is narrower: the Big Five structural pattern is not obviously an artifact of any one of the major observed demographic strata tested here.

Exact metrics are in `demographic_stratification_sensitivity.csv`.
