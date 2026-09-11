(function () {
  "use strict";

  const DATA = window.TRAIT_PROFILE_GEOMETRY_DATA;
  const LOPO = window.TRAIT_PROFILE_LOPO_MODELS;
  const Core = window.TraitProfileGeometryCore;
  const PC_NAMES = ["PC1", "PC2", "PC3"];
  const CLUSTER_COLORS = {
    editorial: "#e8b84b",
    procedural_professional: "#4a9eff",
    grounded_social: "#5ecb8a",
    combative_iconoclast: "#ff766f",
    trickster_chaos: "#b98cff",
    mythic_spiritual: "#38cfc2",
    other: "#f472b6"
  };
  const state = {
    selectedIndex: -1,
    baselineProfile: [],
    baselinePercentiles: [],
    currentProfile: [],
    currentPercentiles: [],
    changed: new Set(),
    prediction: [0, 0, 0],
    ood: null,
    view: "3d",
    axes: [0, 1],
    camera: null,
    rows: [],
    rendering: false
  };

  const byId = (id) => document.getElementById(id);
  const fmt = (value, digits = 3) => Number(value).toFixed(digits);
  const safeColor = (cluster) => CLUSTER_COLORS[cluster] || "#8293a8";

  function currentPersona() {
    return DATA.personas[state.selectedIndex];
  }

  function buildPersonaOptions() {
    const fragment = document.createDocumentFragment();
    for (const persona of DATA.personas) {
      const option = document.createElement("option");
      option.value = persona.name;
      fragment.appendChild(option);
    }
    byId("persona-options").appendChild(fragment);
  }

  function buildTraitControls() {
    const fragment = document.createDocumentFragment();
    DATA.traits.forEach((trait, index) => {
      const row = document.createElement("div");
      row.className = "trait-row";
      row.dataset.index = String(index);
      row.dataset.name = trait.name.toLowerCase();

      const name = document.createElement("div");
      name.className = "trait-name";
      const detailButton = document.createElement("button");
      detailButton.type = "button";
      detailButton.textContent = trait.name;
      detailButton.setAttribute("aria-label", `Show definition for ${trait.name}`);
      detailButton.addEventListener("click", () => {
        byId("trait-detail").textContent = trait.definition
          ? `${trait.name}: ${trait.definition}`
          : `${trait.name}: no canonical definition is available.`;
      });
      name.appendChild(detailButton);

      const slider = document.createElement("input");
      slider.type = "range";
      slider.min = "0";
      slider.max = "100";
      slider.step = "0.1";
      slider.setAttribute("aria-label", `${trait.name} percentile`);
      slider.addEventListener("input", () => setTraitPercentile(index, Number(slider.value), true));

      const value = document.createElement("output");
      value.className = "trait-value";
      value.setAttribute("aria-label", `${trait.name} current percentile`);

      const reset = document.createElement("button");
      reset.type = "button";
      reset.className = "row-reset";
      reset.textContent = "↺";
      reset.setAttribute("aria-label", `Reset ${trait.name}`);
      reset.addEventListener("click", () => resetTrait(index));

      row.append(name, slider, value, reset);
      state.rows.push({ row, slider, value });
      fragment.appendChild(row);
    });
    byId("trait-list").appendChild(fragment);
  }

  function setTraitPercentile(indexOrName, percentile, refresh) {
    const index = typeof indexOrName === "string"
      ? DATA.traits.findIndex((trait) => trait.name === indexOrName)
      : indexOrName;
    if (index < 0 || index >= DATA.traits.length) throw new Error(`Unknown trait: ${indexOrName}`);
    const clamped = Math.min(Math.max(Number(percentile), 0), 100);
    const references = DATA.ood_reference.percentile_reference.sorted_raw_values_by_trait[index];
    state.currentPercentiles[index] = clamped;
    state.currentProfile[index] = Core.empiricalQuantile(references, clamped);
    if (Math.abs(state.currentProfile[index] - state.baselineProfile[index]) > 1e-14) state.changed.add(index);
    else state.changed.delete(index);
    updateTraitRow(index);
    if (refresh !== false) updatePrediction();
  }

  function resetTrait(index) {
    state.currentProfile[index] = state.baselineProfile[index];
    state.currentPercentiles[index] = state.baselinePercentiles[index];
    state.changed.delete(index);
    updateTraitRow(index);
    updatePrediction();
  }

  function resetAll() {
    state.currentProfile = state.baselineProfile.slice();
    state.currentPercentiles = state.baselinePercentiles.slice();
    state.changed.clear();
    state.rows.forEach((_, index) => updateTraitRow(index));
    updatePrediction();
  }

  function updateTraitRow(index) {
    const entry = state.rows[index];
    const percentile = state.currentPercentiles[index];
    entry.slider.value = String(percentile);
    entry.value.value = fmt(percentile, 1);
    entry.value.textContent = fmt(percentile, 1);
    entry.row.classList.toggle("changed", state.changed.has(index));
  }

  function filterTraits() {
    const query = byId("trait-search").value.trim().toLowerCase();
    const changedOnly = byId("changed-only").checked;
    state.rows.forEach((entry, index) => {
      entry.row.hidden = (query && !entry.row.dataset.name.includes(query)) || (changedOnly && !state.changed.has(index));
    });
  }

  function equalizerPath(percentiles, width, height) {
    const pad = 12;
    return percentiles.map((value, index) => {
      const x = pad + index * ((width - 2 * pad) / (percentiles.length - 1));
      const y = pad + (100 - value) / 100 * (height - 2 * pad);
      return `${index ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`;
    }).join(" ");
  }

  function renderEqualizer() {
    const svg = byId("equalizer-svg");
    const width = Math.max(3120, svg.parentElement.clientWidth);
    const height = 180;
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.style.width = `${width}px`;
    svg.replaceChildren();
    const ns = "http://www.w3.org/2000/svg";
    for (const value of [0, 25, 50, 75, 100]) {
      const y = 12 + (100 - value) / 100 * (height - 24);
      const line = document.createElementNS(ns, "line");
      line.setAttribute("x1", "0"); line.setAttribute("x2", String(width));
      line.setAttribute("y1", String(y)); line.setAttribute("y2", String(y));
      line.setAttribute("stroke", "#29384c"); line.setAttribute("stroke-width", "1");
      svg.appendChild(line);
    }
    const baseline = document.createElementNS(ns, "path");
    baseline.setAttribute("d", equalizerPath(state.baselinePercentiles, width, height));
    baseline.setAttribute("fill", "none"); baseline.setAttribute("stroke", "#708197"); baseline.setAttribute("stroke-width", "1.4");
    baseline.setAttribute("opacity", ".72");
    svg.appendChild(baseline);
    const edited = document.createElementNS(ns, "path");
    edited.setAttribute("d", equalizerPath(state.currentPercentiles, width, height));
    edited.setAttribute("fill", "none"); edited.setAttribute("stroke", "#5de1ff"); edited.setAttribute("stroke-width", "2");
    svg.appendChild(edited);
    for (const index of state.changed) {
      const circle = document.createElementNS(ns, "circle");
      const x = 12 + index * ((width - 24) / (DATA.traits.length - 1));
      const y = 12 + (100 - state.currentPercentiles[index]) / 100 * (height - 24);
      circle.setAttribute("cx", String(x)); circle.setAttribute("cy", String(y)); circle.setAttribute("r", "3.5"); circle.setAttribute("fill", "#ffdf5d");
      const title = document.createElementNS(ns, "title");
      title.textContent = `${DATA.traits[index].name}: ${fmt(state.currentPercentiles[index], 1)} percentile`;
      circle.appendChild(title);
      svg.appendChild(circle);
    }
  }

  function clusterTraces3d() {
    return DATA.clusters.map((cluster) => {
      const members = DATA.personas.filter((persona) => persona.cluster === cluster);
      return {
        type: "scatter3d", mode: "markers", name: cluster.replaceAll("_", " "),
        x: members.map((p) => p.coordinate[0]), y: members.map((p) => p.coordinate[1]), z: members.map((p) => p.coordinate[2]),
        text: members.map((p) => p.name), customdata: members.map((p) => p.name),
        hovertemplate: "%{text}<br>PC1 %{x:.2f}<br>PC2 %{y:.2f}<br>PC3 %{z:.2f}<extra>%{fullData.name}</extra>",
        marker: { size: 4.8, color: safeColor(cluster), opacity: .7 }
      };
    });
  }

  function clusterTraces2d() {
    const [xIndex, yIndex] = state.axes;
    return DATA.clusters.map((cluster) => {
      const members = DATA.personas.filter((persona) => persona.cluster === cluster);
      return {
        type: "scattergl", mode: "markers", name: cluster.replaceAll("_", " "),
        x: members.map((p) => p.coordinate[xIndex]), y: members.map((p) => p.coordinate[yIndex]),
        text: members.map((p) => p.name), customdata: members.map((p) => p.name),
        hovertemplate: `%{text}<br>${PC_NAMES[xIndex]} %{x:.2f}<br>${PC_NAMES[yIndex]} %{y:.2f}<extra>%{fullData.name}</extra>`,
        marker: { size: 7, color: safeColor(cluster), opacity: .72 }
      };
    });
  }

  function q95() {
    return PC_NAMES.map((pc) => DATA.error_reference[pc].q95_absolute_error);
  }

  function specialTraces3d(actual, predicted) {
    const traces = [{
      type: "scatter3d", mode: "lines", name: "actual → predicted", showlegend: false,
      x: [actual[0], predicted[0]], y: [actual[1], predicted[1]], z: [actual[2], predicted[2]],
      hoverinfo: "skip", line: { color: "rgba(255,223,93,.58)", width: 4 }
    }, {
      type: "scatter3d", mode: "markers+text", name: "selected actual", showlegend: false,
      x: [actual[0]], y: [actual[1]], z: [actual[2]], text: [`${currentPersona().name} actual`], textposition: "top center",
      hovertemplate: "%{text}<br>PC1 %{x:.3f}<br>PC2 %{y:.3f}<br>PC3 %{z:.3f}<extra></extra>",
      marker: { size: 9, color: "#ffffff", symbol: "diamond", line: { color: "#080d14", width: 2 } }
    }, {
      type: "scatter3d", mode: "markers+text", name: "held-out predicted", showlegend: false,
      x: [predicted[0]], y: [predicted[1]], z: [predicted[2]], text: [state.changed.size ? "predicted counterfactual" : "held-out prediction"], textposition: "bottom center",
      hovertemplate: "%{text}<br>PC1 %{x:.3f}<br>PC2 %{y:.3f}<br>PC3 %{z:.3f}<extra></extra>",
      marker: { size: 10, color: "#ffdf5d", symbol: "circle", line: { color: "#080d14", width: 2 } }
    }];
    if (byId("show-error").checked) {
      const error = q95();
      for (let axis = 0; axis < 3; axis += 1) {
        const low = predicted.slice(); const high = predicted.slice();
        low[axis] -= error[axis]; high[axis] += error[axis];
        traces.push({
          type: "scatter3d", mode: "lines", showlegend: false, hoverinfo: "skip",
          x: [low[0], high[0]], y: [low[1], high[1]], z: [low[2], high[2]],
          line: { color: "rgba(255,223,93,.38)", width: 6 }
        });
      }
    }
    return traces;
  }

  function specialTraces2d(actual, predicted) {
    const [xIndex, yIndex] = state.axes;
    const actual2 = Core.projectAxes(actual, state.axes);
    const predicted2 = Core.projectAxes(predicted, state.axes);
    const error = q95();
    return [{
      type: "scatter", mode: "lines", showlegend: false, hoverinfo: "skip",
      x: [actual2[0], predicted2[0]], y: [actual2[1], predicted2[1]], line: { color: "rgba(255,223,93,.58)", width: 2 }
    }, {
      type: "scatter", mode: "markers+text", showlegend: false,
      x: [actual2[0]], y: [actual2[1]], text: [`${currentPersona().name} actual`], textposition: "top center",
      hovertemplate: `%{text}<br>${PC_NAMES[xIndex]} %{x:.3f}<br>${PC_NAMES[yIndex]} %{y:.3f}<extra></extra>`,
      marker: { size: 13, color: "#ffffff", symbol: "diamond", line: { color: "#080d14", width: 2 } }
    }, {
      type: "scatter", mode: "markers+text", showlegend: false,
      x: [predicted2[0]], y: [predicted2[1]], text: [state.changed.size ? "predicted counterfactual" : "held-out prediction"], textposition: "bottom center",
      hovertemplate: `%{text}<br>${PC_NAMES[xIndex]} %{x:.3f}<br>${PC_NAMES[yIndex]} %{y:.3f}<extra></extra>`,
      marker: { size: 14, color: "#ffdf5d", symbol: "circle", line: { color: "#080d14", width: 2 } },
      error_x: { type: "constant", value: error[xIndex], visible: byId("show-error").checked, color: "rgba(255,223,93,.65)", thickness: 1.2 },
      error_y: { type: "constant", value: error[yIndex], visible: byId("show-error").checked, color: "rgba(255,223,93,.65)", thickness: 1.2 }
    }];
  }

  function plotLayout() {
    const common = {
      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", font: { color: "#dce6f1", size: 11 },
      margin: { l: 52, r: 18, t: 12, b: 48 }, legend: { orientation: "h", y: 1.04 }, hovermode: "closest", uirevision: "trait-profile-equalizer"
    };
    if (state.view === "3d") {
      common.scene = {
        xaxis: { title: "PC1", gridcolor: "#29384c", zerolinecolor: "#41536a" },
        yaxis: { title: "PC2", gridcolor: "#29384c", zerolinecolor: "#41536a" },
        zaxis: { title: "PC3", gridcolor: "#29384c", zerolinecolor: "#41536a" },
        bgcolor: "rgba(0,0,0,0)", aspectmode: "data", uirevision: "trait-profile-equalizer-3d"
      };
      if (state.camera) common.scene.camera = state.camera;
    } else {
      common.xaxis = { title: PC_NAMES[state.axes[0]], gridcolor: "#29384c", zerolinecolor: "#41536a" };
      common.yaxis = { title: PC_NAMES[state.axes[1]], gridcolor: "#29384c", zerolinecolor: "#41536a", scaleanchor: null };
    }
    return common;
  }

  function renderPlot() {
    if (!window.Plotly) throw new Error("Plotly failed to load");
    const persona = currentPersona();
    const traces = state.view === "3d"
      ? clusterTraces3d().concat(specialTraces3d(persona.coordinate, state.prediction))
      : clusterTraces2d().concat(specialTraces2d(persona.coordinate, state.prediction));
    state.rendering = true;
    return Plotly.react("geometry-plot", traces, plotLayout(), {
      responsive: true, displaylogo: false, scrollZoom: true, modeBarButtonsToRemove: ["lasso2d", "select2d"]
    }).then(() => { state.rendering = false; });
  }

  function updateMetrics() {
    const actual = currentPersona().coordinate;
    const delta = state.prediction.map((value, index) => value - actual[index]);
    byId("pc1-value").textContent = fmt(state.prediction[0]);
    byId("pc2-value").textContent = fmt(state.prediction[1]);
    byId("pc3-value").textContent = fmt(state.prediction[2]);
    byId("delta-value").textContent = delta.map((value) => `${value >= 0 ? "+" : ""}${fmt(value)}`).join(" / ");
    byId("distance-value").textContent = fmt(Core.euclidean(state.prediction, actual));
    byId("changed-count").textContent = String(state.changed.size);
    byId("ood-label").textContent = state.ood.heuristic_label;
    byId("ood-distance").textContent = fmt(state.ood.mean_5nn_distance);
    byId("ood-percentile").textContent = `${fmt(state.ood.distance_percentile_vs_canonical_loo, 1)}th`;
    byId("ood-outside").textContent = String(state.ood.traits_outside_training_range_count);
    const list = byId("neighbor-list");
    list.replaceChildren();
    state.ood.nearest_personas.forEach((neighbor) => {
      const item = document.createElement("li");
      item.textContent = `${neighbor.persona} — ${fmt(neighbor.distance)}`;
      list.appendChild(item);
    });
    filterTraits();
  }

  function updatePrediction() {
    const persona = currentPersona();
    state.prediction = Core.predictRidge(state.currentProfile, LOPO[persona.name]);
    state.ood = Core.oodDiagnostic(state.currentProfile, DATA.ood_reference, persona.name);
    updateMetrics();
    renderEqualizer();
    return renderPlot();
  }

  function selectPersona(name) {
    const index = DATA.personas.findIndex((persona) => persona.name === name);
    if (index < 0) throw new Error(`Unknown persona: ${name}`);
    state.selectedIndex = index;
    const persona = DATA.personas[index];
    state.baselineProfile = persona.profile.slice();
    state.baselinePercentiles = Core.profileToPercentiles(
      state.baselineProfile,
      DATA.ood_reference.percentile_reference.sorted_raw_values_by_trait
    );
    state.currentProfile = state.baselineProfile.slice();
    state.currentPercentiles = state.baselinePercentiles.slice();
    state.changed.clear();
    byId("persona-input").value = persona.name;
    state.rows.forEach((_, traitIndex) => updateTraitRow(traitIndex));
    return updatePrediction();
  }

  function setView(view) {
    if (view !== "2d" && view !== "3d") throw new Error(`Unknown view: ${view}`);
    state.view = view;
    byId("view-2d").setAttribute("aria-pressed", String(view === "2d"));
    byId("view-3d").setAttribute("aria-pressed", String(view === "3d"));
    byId("axis-controls").hidden = view !== "2d";
    return renderPlot();
  }

  function setAxes(x, y) {
    if (x === y) throw new Error("2D axes must differ");
    state.axes = [Number(x), Number(y)];
    byId("x-axis").value = String(x);
    byId("y-axis").value = String(y);
    return state.view === "2d" ? renderPlot() : Promise.resolve();
  }

  function snapshot() {
    const persona = currentPersona();
    return {
      persona: persona.name,
      actual: persona.coordinate.slice(),
      prediction: state.prediction.slice(),
      projected_prediction: Core.projectAxes(state.prediction, state.axes),
      projected_actual: Core.projectAxes(persona.coordinate, state.axes),
      axes: state.axes.slice(),
      view: state.view,
      changed_traits: Array.from(state.changed).map((index) => DATA.traits[index].name),
      current_profile: state.currentProfile.slice(),
      current_percentiles: state.currentPercentiles.slice(),
      baseline_profile: state.baselineProfile.slice(),
      ood: JSON.parse(JSON.stringify(state.ood)),
      camera: state.camera ? JSON.parse(JSON.stringify(state.camera)) : null
    };
  }

  function wireEvents() {
    byId("load-persona").addEventListener("click", () => {
      const name = byId("persona-input").value.trim();
      if (DATA.personas.some((persona) => persona.name === name)) selectPersona(name);
      else byId("app-status").textContent = `Unknown persona: ${name}`;
    });
    byId("persona-input").addEventListener("keydown", (event) => {
      if (event.key === "Enter") byId("load-persona").click();
    });
    byId("view-3d").addEventListener("click", () => setView("3d"));
    byId("view-2d").addEventListener("click", () => setView("2d"));
    byId("x-axis").addEventListener("change", () => {
      let x = Number(byId("x-axis").value); let y = Number(byId("y-axis").value);
      if (x === y) { y = (x + 1) % 3; byId("y-axis").value = String(y); }
      setAxes(x, y);
    });
    byId("y-axis").addEventListener("change", () => {
      let x = Number(byId("x-axis").value); let y = Number(byId("y-axis").value);
      if (x === y) { x = (y + 1) % 3; byId("x-axis").value = String(x); }
      setAxes(x, y);
    });
    byId("show-error").addEventListener("change", renderPlot);
    byId("trait-search").addEventListener("input", filterTraits);
    byId("changed-only").addEventListener("change", filterTraits);
    byId("reset-all").addEventListener("click", resetAll);
    const plot = byId("geometry-plot");
    plot.on("plotly_click", (event) => {
      const name = event.points && event.points[0] && event.points[0].customdata;
      if (typeof name === "string" && LOPO[name]) selectPersona(name);
    });
    plot.on("plotly_relayout", (event) => {
      if (!state.rendering && event["scene.camera"]) state.camera = event["scene.camera"];
    });
  }

  function initialize() {
    if (!DATA || !LOPO || !Core) throw new Error("Saved viewer bundle is incomplete");
    if (DATA.personas.length !== 275 || DATA.traits.length !== 240 || Object.keys(LOPO).length !== 275) {
      throw new Error("Expected 275 personas, 240 traits, and 275 held-out models");
    }
    buildPersonaOptions();
    buildTraitControls();
    const errors = PC_NAMES.map((pc) => `${pc} ±${fmt(DATA.error_reference[pc].q95_absolute_error)}`);
    byId("error-reference").textContent = errors.join("; ");
    const initial = DATA.personas.some((persona) => persona.name === "therapist") ? "therapist" : DATA.personas[0].name;
    selectPersona(initial).then(() => {
      wireEvents();
      byId("app-status").dataset.ready = "true";
      byId("app-status").textContent = "Ready · saved artifacts only · no model inference";
      window.dispatchEvent(new CustomEvent("trait-equalizer-ready"));
    }).catch(showFatal);
  }

  function showFatal(error) {
    const status = byId("app-status");
    status.dataset.ready = "false";
    status.textContent = `Viewer error: ${error.message}`;
    console.error(error);
  }

  window.__TRAIT_EQUALIZER_TEST__ = {
    data: () => DATA,
    models: () => LOPO,
    resetAll,
    selectPersona,
    setAxes,
    setTraitPercentile,
    setView,
    snapshot,
    updatePrediction
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
  else initialize();
})();
