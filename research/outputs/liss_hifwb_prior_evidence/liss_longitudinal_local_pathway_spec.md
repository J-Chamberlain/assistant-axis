# Minimum viable longitudinal local-pathway specification

## Estimand
Estimate whether a within-person deviation in a modifiable behavior/context at time t predicts change in a prespecified wellbeing outcome at t+1, conditional on prior wellbeing and stable personality, and whether that association varies by the baseline personality profile.

## Minimal model
`W_(i,t+1) ~ W_(i,t) + T_i + B_(i,t) + within(B_(i,t)) + T_i×within(B_(i,t)) + C_(i,t) + time + interval + person effect`

Start with one behavior and one wellbeing outcome per preregistered model. Person-mean center repeated behaviors to separate within-person change from between-person differences. Include prior wellbeing, interval length, time, and a small defensible confounder set. Use random intercepts or person fixed effects; choose based on the estimand and data support.

## Model ladder

- Multilevel/fixed-effects regression is the default minimum.
- Latent change models are appropriate when repeated measurement models are stable and change is the estimand.
- RI-CLPM is useful for reciprocal within-person lagged questions with at least three comparable waves.
- Dynamic SEM requires enough dense, regular observations and is not the default.
- Doubly robust or weighting methods require measured-confounder, positivity, and treatment-consistency arguments.

## Gates
Exact repeated measures, temporal overlap, attrition, measurement invariance, sample size for interactions, and plausible confounder coverage must pass before estimation. Static density is not a transition probability. Prediction and moderation do not establish causal benefit.
