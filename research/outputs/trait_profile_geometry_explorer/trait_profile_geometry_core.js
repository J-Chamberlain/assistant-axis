(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.TraitProfileGeometryCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function dot(a, b) {
    let total = 0;
    for (let i = 0; i < a.length; i += 1) total += a[i] * b[i];
    return total;
  }

  function euclidean(a, b) {
    let total = 0;
    for (let i = 0; i < a.length; i += 1) {
      const delta = a[i] - b[i];
      total += delta * delta;
    }
    return Math.sqrt(total);
  }

  function lowerBound(values, target) {
    let low = 0;
    let high = values.length;
    while (low < high) {
      const middle = (low + high) >> 1;
      if (values[middle] < target) low = middle + 1;
      else high = middle;
    }
    return low;
  }

  function upperBound(values, target) {
    let low = 0;
    let high = values.length;
    while (low < high) {
      const middle = (low + high) >> 1;
      if (values[middle] <= target) low = middle + 1;
      else high = middle;
    }
    return low;
  }

  // Exact browser counterpart of predict_trait_profile.py::percentile_of_reference.
  function percentileOfReference(value, sortedReference) {
    if (!sortedReference.length) return NaN;
    if (sortedReference.length === 1) return value >= sortedReference[0] ? 100 : 0;
    const left = lowerBound(sortedReference, value);
    const right = upperBound(sortedReference, value);
    const averageIndex = (left + right - 1) / 2;
    return 100 * Math.min(Math.max(averageIndex / (sortedReference.length - 1), 0), 1);
  }

  // Exact browser counterpart of predict_trait_profile.py::empirical_quantile.
  function empiricalQuantile(sortedValues, percentile) {
    if (percentile < 0 || percentile > 100) throw new Error(`Percentile outside [0, 100]: ${percentile}`);
    if (sortedValues.length === 1) return sortedValues[0];
    const position = percentile / 100 * (sortedValues.length - 1);
    const lower = Math.floor(position);
    const upper = Math.ceil(position);
    if (lower === upper) return sortedValues[lower];
    const weight = position - lower;
    return (1 - weight) * sortedValues[lower] + weight * sortedValues[upper];
  }

  function profileToPercentiles(profile, references) {
    return profile.map((value, index) => percentileOfReference(value, references[index]));
  }

  function percentilesToProfile(percentiles, references) {
    return percentiles.map((value, index) => empiricalQuantile(references[index], value));
  }

  function predictRidge(profile, model) {
    const direct = model.portable_prediction ? model.portable_prediction.raw_input_to_pc : model.raw_input_to_pc;
    return direct.coefficients.map((row, index) => dot(row, profile) + direct.intercepts[index]);
  }

  function standardizedFeatures(profile, transform) {
    return profile.map((value, index) => (value - transform.mean[index]) / transform.scale[index]);
  }

  function projectProfile(profile, ood) {
    const scaled = standardizedFeatures(profile, ood.feature_standardizer);
    const centered = scaled.map((value, index) => value - ood.profile_pca.mean[index]);
    return ood.profile_pca.components.map((component) => dot(component, centered));
  }

  function reconstructionError(profile, ood) {
    const scaled = standardizedFeatures(profile, ood.feature_standardizer);
    const centered = scaled.map((value, index) => value - ood.profile_pca.mean[index]);
    const scores = ood.profile_pca.components.map((component) => dot(component, centered));
    const reconstructed = centered.map((_, index) => {
      let value = 0;
      for (let j = 0; j < scores.length; j += 1) value += scores[j] * ood.profile_pca.components[j][index];
      return value;
    });
    return euclidean(centered, reconstructed);
  }

  function oodDiagnostic(profile, ood, excludeName) {
    const score = projectProfile(profile, ood);
    const distances = [];
    for (let i = 0; i < ood.training_personas.length; i += 1) {
      const name = ood.training_personas[i];
      if (name !== excludeName) distances.push([euclidean(score, ood.training_profile_pca_scores[i]), name]);
    }
    distances.sort((a, b) => a[0] - b[0] || a[1].localeCompare(b[1]));
    if (!distances.length) throw new Error("No training profiles remain for OOD comparison");
    const nearestPersonas = distances.slice(0, 5).map(([distance, persona]) => ({ persona, distance }));
    const k5 = Math.min(5, distances.length);
    let mean5nn = 0;
    for (let i = 0; i < k5; i += 1) mean5nn += distances[i][0];
    mean5nn /= k5;
    const distancePercentile = percentileOfReference(mean5nn, ood.reference_distances.loo_mean_5nn_sorted);
    const pcaError = reconstructionError(profile, ood);
    const reconstructionPercentile = percentileOfReference(
      pcaError,
      ood.reference_distances.profile_pca_reconstruction_error_sorted
    );
    const outside = [];
    for (let i = 0; i < profile.length; i += 1) {
      if (profile[i] < ood.training_feature_ranges.min[i] || profile[i] > ood.training_feature_ranges.max[i]) {
        outside.push(ood.trait_feature_names[i]);
      }
    }
    let label = "in-distribution";
    if (distancePercentile > 99 || reconstructionPercentile > 99 || outside.length >= 5) {
      label = "out-of-distribution";
    } else if (distancePercentile > 90 || reconstructionPercentile > 90 || outside.length) {
      label = "edge-of-distribution";
    }
    return {
      heuristic_label: label,
      nearest_neighbor_distance: distances[0][0],
      mean_5nn_distance: mean5nn,
      distance_percentile_vs_canonical_loo: distancePercentile,
      profile_pca_reconstruction_error: pcaError,
      reconstruction_error_percentile_vs_canonical: reconstructionPercentile,
      traits_outside_training_range_count: outside.length,
      traits_outside_training_range: outside,
      nearest_personas: nearestPersonas,
      note: "Heuristic profile-geometry diagnostic, not a calibrated probability."
    };
  }

  function projectAxes(point, axes) {
    return [point[axes[0]], point[axes[1]]];
  }

  function maxAbsDifference(a, b) {
    let maximum = 0;
    for (let i = 0; i < a.length; i += 1) maximum = Math.max(maximum, Math.abs(a[i] - b[i]));
    return maximum;
  }

  return {
    dot,
    empiricalQuantile,
    euclidean,
    maxAbsDifference,
    oodDiagnostic,
    percentileOfReference,
    percentilesToProfile,
    predictRidge,
    profileToPercentiles,
    projectAxes,
    projectProfile,
    reconstructionError,
    standardizedFeatures
  };
});
