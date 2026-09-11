#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const Core = require("./trait_profile_geometry_core.js");
const here = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(here, "trait_profile_geometry_data.json"), "utf8"));
const bundle = JSON.parse(fs.readFileSync(path.join(here, "lopo_ridge_predictors.json"), "utf8"));
const references = JSON.parse(fs.readFileSync(path.join(here, "browser_python_reference_cases.json"), "utf8"));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function maxAbs(a, b) {
  return Math.max(...a.map((value, index) => Math.abs(value - b[index])));
}

assert(data.personas.length === 275, "Expected all 275 personas");
assert(data.traits.length === 240, "Expected all 240 traits");
assert(new Set(data.traits.map((trait) => trait.name)).size === 240, "Duplicate traits");
assert(Object.keys(bundle.models).length === 275, "Expected 275 held-out Ridge bundles");
assert(JSON.stringify(data.traits.map((trait) => trait.name)) === JSON.stringify(bundle.trait_feature_names), "Feature order mismatch");

let maxLopo = 0;
for (const persona of data.personas) {
  const model = bundle.models[persona.name];
  assert(model.excluded_persona === persona.name, `Holdout mismatch for ${persona.name}`);
  assert(model.training_persona_count === 274, `Training count mismatch for ${persona.name}`);
  const prediction = Core.predictRidge(persona.profile, model);
  maxLopo = Math.max(maxLopo, maxAbs(prediction, persona.saved_lopo_prediction));
}

let maxPercentile = 0;
let maxPrediction = 0;
let maxOod = 0;
let maxProjection = 0;
const personaMap = Object.fromEntries(data.personas.map((persona) => [persona.name, persona]));
const sortedReferences = data.ood_reference.percentile_reference.sorted_raw_values_by_trait;
for (const testCase of references.cases) {
  const persona = personaMap[testCase.persona];
  const modified = persona.profile.slice();
  for (const edit of testCase.edits) {
    const percentile = Core.percentileOfReference(persona.profile[edit.trait_index], sortedReferences[edit.trait_index]);
    maxPercentile = Math.max(maxPercentile, Math.abs(percentile - edit.baseline_percentile));
    const raw = Core.empiricalQuantile(sortedReferences[edit.trait_index], edit.modified_percentile);
    maxPercentile = Math.max(maxPercentile, Math.abs(raw - edit.modified_raw_cosine));
    modified[edit.trait_index] = raw;
  }
  const firstPrediction = Core.predictRidge(modified, bundle.models[testCase.persona]);
  const secondPrediction = Core.predictRidge(modified.slice(), bundle.models[testCase.persona]);
  maxPrediction = Math.max(maxPrediction, maxAbs(firstPrediction, testCase.expected_prediction), maxAbs(firstPrediction, secondPrediction));
  const observedOod = Core.oodDiagnostic(modified, data.ood_reference, testCase.persona);
  const expectedOod = testCase.expected_ood;
  for (const key of [
    "nearest_neighbor_distance",
    "mean_5nn_distance",
    "distance_percentile_vs_canonical_loo",
    "profile_pca_reconstruction_error",
    "reconstruction_error_percentile_vs_canonical"
  ]) maxOod = Math.max(maxOod, Math.abs(observedOod[key] - expectedOod[key]));
  assert(observedOod.heuristic_label === expectedOod.heuristic_label, `OOD label mismatch for ${testCase.case_id}`);
  assert(JSON.stringify(observedOod.traits_outside_training_range) === JSON.stringify(expectedOod.traits_outside_training_range), `OOD ranges mismatch for ${testCase.case_id}`);
  for (const axes of [[0, 1], [0, 2], [1, 2]]) {
    const projected = Core.projectAxes(firstPrediction, axes);
    maxProjection = Math.max(maxProjection, Math.abs(projected[0] - firstPrediction[axes[0]]), Math.abs(projected[1] - firstPrediction[axes[1]]));
  }
}

const report = {
  schema_version: "1.0",
  test_type: "Node.js browser-core numerical verification (not a live browser)",
  reference_case_count: references.cases.length,
  maximum_lopo_reproduction_error: maxLopo,
  maximum_percentile_inverse_mapping_error: maxPercentile,
  maximum_modified_prediction_python_agreement_error: maxPrediction,
  maximum_ood_python_agreement_error: maxOod,
  maximum_2d_projection_error: maxProjection,
  passed: references.cases.length >= 25 && maxLopo <= 1e-9 && maxPercentile <= 1e-12 && maxPrediction <= 1e-9 && maxOod <= 1e-9 && maxProjection === 0
};
fs.writeFileSync(path.join(here, "node_verification_report.json"), JSON.stringify(report, null, 2) + "\n");
process.stdout.write(JSON.stringify(report, null, 2) + "\n");
if (!report.passed) process.exit(1);
