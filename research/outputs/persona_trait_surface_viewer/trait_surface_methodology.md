# Five-Group Qwen Trait Landscape

Date: 2026-09-09 (America/Los_Angeles)
Startup: canonical raw manifest and three startup files fetched in order and verified against local content, SHA256 and byte counts before implementation.
Base commit: 03d99df on master.
Status: implemented; data, camera-math and UI-state tests pass. New live-browser/WebGL verification unavailable because browser-use policy blocked the local URL. The block was not bypassed.

## Open and Use

Open [persona_trait_surface_viewer.html](persona_trait_surface_viewer.html), not `viewer_template.html`. The completed file embeds Plotly, the prepared data, camera math and UI; it has no external chart/data dependency. It is a separate companion and does not replace the working emotion landscape or either ridge viewer.

Select two distinct PCs for the horizontal plane and use the five-stop group slider or group buttons for height. All six ordered PC pairs are available. Reversing the axes transposes an existing surface rather than changing the scores or fitting a new PCA.

New controls:

- **Stronger height colors:** saturated blue through cyan, pale cream, yellow/orange and red; fixed 0-100 range and numeric colorbar across every group. The midpoint 50 is the population mean. Fabric opacity is 1 with more ambient lighting to reduce washed-out shading. Color means only height, not valence, goodness, assistantness or group identity.
- **Persona nodes:** uncheck to hide exact nodes, pinned labels, node-to-fabric connectors and the faint mean-reference plane. Only the fabric/weave and axes remain. The persona selector still gives exact scores in the side panel. Restoring nodes restores the current selection. Connector controls are disabled while nodes/fabric are hidden.
- **Orientation dials:** yaw (horizontal rotation), pitch (tilt), roll and zoom, each with a slider, a visual dial indicator and exact numeric entry. Rotation/roll span -180 to 180 degrees, tilt -90 to 90, zoom 25-300 percent. Higher zoom means a closer camera. Angles and numbers synchronize after mouse camera changes; the existing mouse-drag/wheel controls remain available.
- **View presets:** Isometric, Top, Front and Side recenter the scene. Reset view restores the original camera. Individual dial changes preserve any mouse-adjusted camera center; changing group, axes or smoothing preserves orientation/zoom. Camera updates are coalesced so rapid changes end at the latest requested setting.

The side panel lists the selected group's three constituent trait percentiles, group mean, mean member z-score, the original selected PC coordinates, and the fitted-surface gap. Smoothness still offers Detail, Balanced and Gentle; smoothing never changes exact nodes.

## Group Definition

These are the same 15 traits and editorial groups already used in the ridge plots, not newly selected or fitted factors:

| Group | Three members |
|---|---|
| Exploration | creative, abstract, curious |
| Response | reactive, adaptable, practical |
| Scrutiny | skeptical, analytical, conscientious |
| Challenge | rebellious, competitive, manipulative |
| Affiliation | empathetic, agreeable, altruistic |

For persona i and group g, `height(i,g) = mean(member_trait_percentiles(i,g))`, with three equal weights of 1/3. Member percentiles come unchanged from `persona_trait_ridge_data.json`: `100 * (average_rank(raw_cosine) - 0.5) / 275`, independently within each trait. Every group's across-persona mean is therefore 50, but its variance depends on how its three members co-vary. We do not re-rank or re-standardize the composite, normalize within a persona, fit weights or apply softmax. A group mean of 80 is an average of three trait percentiles, not necessarily the 80th percentile of the group composite.

The supplemental mean member z-score is the average of three independently standardized trait cosines. It is not itself a unit-variance group z-score and is not the rendered height. Group scores cannot establish the prevalence of traits, absolute psychological strength or subjective experience.

## Exact Sources and Provenance

- [Ridge data](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json): 275 personas, unchanged PCs, 15 raw/z/percentile trait profiles and their editorial group assignments.
- [Ridge category order](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_trait_ridge_plots/trait_category_order.csv) and [manifest](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_trait_ridge_plots/persona_trait_ridge_manifest.json): trait definitions and exact source hashes.
- [Canonical geometry](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/visualizations/geometry_viz_data.json): `roles.names` and `roles.pca3d` must match the ridge data exactly. No refitting, coordinate rescaling in the data, or sign changes.
- [Trait-profile provenance audit](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md): inherited trait definitions and released Qwen activation vectors, with internally computed role-to-trait cosines. The upstream matrix averages each released tensor's 64 rows before normalization. This is same-space activation evidence, not independent psychological ratings or the single-layer emotion readout.
- [Working emotion surface generator](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/run_persona_emotion_surface_viewer.py): inherited thin-plate spline, common PC-distance scale, smoothing choices and hull/density masks. Its viewer interaction pattern was reused in separate sources.

The new [source manifest](trait_surface_manifest.json) records hashes and software details. [Group score CSV](persona_trait_group_scores.csv) contains 1,375 unique persona/group rows, each including its three original trait scores. There are no new activation generations, GPU runs, judge calls or model API calls.

## Fabric Construction and Limits

For each of the three unordered PC planes, use a 61-by-61 grid. Center the two coordinates and divide both by one common scale, `sqrt(mean(var(PCs)))`, preserving relative distance between the axes. Coincident projected points, if any, are combined only for fitting. Fit a degree-1 thin-plate RBF with smoothing 0.003, 0.03 or 0.3 for Detail, Balanced or Gentle. Exact persona nodes retain their unchanged source coordinates and group heights.

Mask outside the persona convex hull or where the sixth-neighbor distance exceeds the 90th percentile of persona sixth-neighbor distances. The masks and grid axes match the working emotion surface exactly. This support mask is not a confidence interval. Interpolated fabric is an in-sample descriptive fit, not independently measured trait values between personas.

Percentile composites have a 0-100 support. Fitted fabric values outside that range are clipped to it, including fitted node values used for connector endpoints; exact scored nodes are never clipped or moved. Across all 45 plane/smoothing/group grids, 73 of 74,820 supported grid values require clipping (about 0.10%). Counts and unclipped extrema are preserved in [fit diagnostics](trait_surface_fit_diagnostics.csv). The default PC1-PC2 Balanced view clips five grid cells for Challenge and none for the other groups. Sharp peaks, smoothing choices and sparse cutouts must not be treated as new latent structure.

Default PC1-PC2 Balanced fit gaps, in percentile points RMS: Exploration 6.56, Response 4.98, Scrutiny 5.83, Challenge 8.19, Affiliation 11.84. These describe surface approximation error at observed nodes, not prediction performance. The larger Affiliation gap is a reason to inspect the exact nodes before interpreting fabric contours. Vertical display aspect is chosen for readability and is not commensurate with horizontal PC units.

The user's visually inverse PC1/PC2 ridge observation motivated this viewer; this task does not test or establish a statistical inverse relationship. Averaging three traits can hide disagreement, which is why the constituent scores and original ridges remain available.

## Verification

`verify_trait_surface_data.py`: exact geometry and member scores, 1,375 group rows, equal-weight means, population group means of 50, all 45 bounded grids, matching hull/density masks, consistent fit errors, embedded data and source hashes.

`verify_trait_surface_controls.cjs`: 225 yaw/pitch/roll/zoom round-trips and pole checks; five groups; six ordered planes; exact 275-node traces; fabric-only visibility of all relevant traces; numeric entry; preset/reset behavior; drag-event control synchronization; camera persistence across axes/group/smoothing changes; concurrent/rapid camera and group updates. Uses a Plotly/DOM double: this checks UI state and pure camera math, not WebGL rendering.

Browser-use rejected the attempted local-file opening. No alternate browser, localhost proxy, CDP or native-app workaround was attempted. Consequently no new interactive browser screenshot is claimed. `trait_surface_preview.png` is explicitly a **static orthographic scientific rendering of prepared surfaces**, generated with pure SVG/Sharp, not a screenshot or simulated browser UI. Its five surfaces were visually inspected; the actual interactive appearance remains for user inspection in the completed HTML.

## Reproduction

```sh
python3 -B research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py
python3 -B research/outputs/persona_trait_surface_viewer/verify_trait_surface_data.py
node research/outputs/persona_trait_surface_viewer/verify_trait_surface_controls.cjs
node research/outputs/persona_trait_surface_viewer/render_trait_surface_preview.cjs
python3 -B research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py --inventory-only
```

Requires NumPy, SciPy and Plotly for building; Node and Sharp for the optional static preview. Generated HTML itself only needs a JavaScript/WebGL-capable browser. `--html-only` rebuilds UI from existing prepared data; a full build refreshes source hashes after edits. [artifact_inventory.csv](artifact_inventory.csv) enumerates safe output paths, SHA256 checksums and canonical raw URLs.

Project state: new descriptive grouped-trait interface and requested controls, no new scientific claim. CLAIMS_REGISTER and FINDINGS_LEDGER unchanged. No sticky notes directly addressed. Next step: user opens the completed HTML and inspects controls and member-level fidelity before any broader interpretation or new compute.
