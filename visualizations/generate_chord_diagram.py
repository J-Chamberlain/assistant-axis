from __future__ import annotations

import csv
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "connectome-exports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1200
HEIGHT = 1200
CX = WIDTH / 2
CY = HEIGHT / 2
TAU = math.tau

CLUSTER_ORDER = [
    "editorial",
    "procedural_professional",
    "grounded_social",
    "other",
    "combative_iconoclast",
    "trickster_chaos",
    "mythic_spiritual",
]

COLORS = {
    "editorial": "#2166AC",
    "procedural_professional": "#4393C3",
    "grounded_social": "#92C5DE",
    "mythic_spiritual": "#762A83",
    "combative_iconoclast": "#1B7837",
    "trickster_chaos": "#D6604D",
    "other": "#878787",
}

PARCHMENT_COLORS = {
    "editorial": "#4A6741",
    "procedural_professional": "#6B8F71",
    "grounded_social": "#9BB89E",
    "mythic_spiritual": "#7A5C82",
    "combative_iconoclast": "#4A6741",
    "trickster_chaos": "#A0522D",
    "other": "#A09070",
}

PARCHMENT_BALANCE_CLUSTERS = {"editorial", "procedural_professional", "grounded_social"}

BACKGROUND = "#FFFFFF"
PARCHMENT_BACKGROUND = "#F0E8D5"
TEXT_COLOR = "#5B6270"
PARCHMENT_TEXT = "#5C3317"
PERSONA_DOT = "#F3F6FA"

OUTER_RADIUS = 380
ARC_INNER_RADIUS = 342
RIBBON_RADIUS = 332
CENTER_CLEAR_RADIUS = 178
LABEL_RADIUS = 410
DOT_RADIUS = 2.0
CLUSTER_LABEL_RADIUS = 442
CLUSTER_LINE_OFFSET = 22
GROUP_PAD = 0.038
MAX_GROUP_ANGLE = 2 * math.pi / 3
MAX_LABELS_PER_CLUSTER = 8

TITLE_Y = 26
SUBTITLE_Y = 52
TITLE_TEXT = "Persona Connectome"
SUBTITLE_TEXT = "cluster arcs scaled by member count; ribbons widen as centroid distance shrinks"


@dataclass
class Subgroup:
    index: int
    subindex: int
    start_angle: float
    end_angle: float
    value: float


@dataclass
class Group:
    index: int
    start_angle: float
    end_angle: float
    value: float


@dataclass
class Chord:
    source: Subgroup
    target: Subgroup


def rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha:.3f})"


def ribbon_alpha(cluster: str, parchment: bool) -> float:
    if not parchment:
        return 0.30
    return 0.52 if cluster in PARCHMENT_BALANCE_CLUSTERS else 0.14


def polar(radius: float, angle: float) -> tuple[float, float]:
    return CX + radius * math.cos(angle - math.pi / 2), CY + radius * math.sin(angle - math.pi / 2)


def arc_path(start_angle: float, end_angle: float, outer_radius: float, inner_radius: float) -> str:
    start_outer = polar(outer_radius, start_angle)
    end_outer = polar(outer_radius, end_angle)
    end_inner = polar(inner_radius, end_angle)
    start_inner = polar(inner_radius, start_angle)
    large_arc = 1 if end_angle - start_angle > math.pi else 0
    return (
        f"M {start_outer[0]:.3f} {start_outer[1]:.3f} "
        f"A {outer_radius:.3f} {outer_radius:.3f} 0 {large_arc} 1 {end_outer[0]:.3f} {end_outer[1]:.3f} "
        f"L {end_inner[0]:.3f} {end_inner[1]:.3f} "
        f"A {inner_radius:.3f} {inner_radius:.3f} 0 {large_arc} 0 {start_inner[0]:.3f} {start_inner[1]:.3f} Z"
    )


def ribbon_path(source: Subgroup, target: Subgroup, radius: float) -> str:
    sa0 = polar(radius, source.start_angle)
    sa1 = polar(radius, source.end_angle)
    ta0 = polar(radius, target.start_angle)
    ta1 = polar(radius, target.end_angle)
    source_large = 1 if source.end_angle - source.start_angle > math.pi else 0
    target_large = 1 if target.end_angle - target.start_angle > math.pi else 0
    return (
        f"M {sa0[0]:.3f} {sa0[1]:.3f} "
        f"A {radius:.3f} {radius:.3f} 0 {source_large} 1 {sa1[0]:.3f} {sa1[1]:.3f} "
        f"Q {CX:.3f} {CY:.3f} {ta0[0]:.3f} {ta0[1]:.3f} "
        f"A {radius:.3f} {radius:.3f} 0 {target_large} 1 {ta1[0]:.3f} {ta1[1]:.3f} "
        f"Q {CX:.3f} {CY:.3f} {sa0[0]:.3f} {sa0[1]:.3f} Z"
    )


def text_transform(angle: float, radius: float, flip_threshold: float = math.pi) -> tuple[float, float, float, str]:
    x, y = polar(radius, angle)
    deg = math.degrees(angle - math.pi / 2)
    anchor = "start"
    if math.pi / 2 < angle < 3 * math.pi / 2:
        deg += 180
        anchor = "end"
    return x, y, deg, anchor


def mpl_anchor(anchor: str) -> str:
    return {"start": "left", "end": "right", "middle": "center"}.get(anchor, anchor)


def load_full_ranking() -> list[dict[str, str]]:
    with (BASE / "full_ranking.csv").open() as f:
        return list(csv.DictReader(f))


def load_cluster_distances() -> dict[str, dict[str, float]]:
    with (BASE / "cluster_distance_matrix.csv").open() as f:
        rows = list(csv.DictReader(f))
    out: dict[str, dict[str, float]] = {}
    for row in rows:
        label = row["cluster_label"]
        out[label] = {cluster: float(row[cluster]) for cluster in CLUSTER_ORDER}
    return out


def capped_arc_proportions(counts: dict[str, int], max_share: float) -> dict[str, float]:
    total = sum(counts.values())
    remaining = set(CLUSTER_ORDER)
    shares = {cluster: counts[cluster] / total for cluster in CLUSTER_ORDER}
    assigned = {cluster: 0.0 for cluster in CLUSTER_ORDER}
    available = 1.0

    while remaining:
        rem_total = sum(counts[c] for c in remaining)
        changed = False
        for cluster in list(remaining):
            share = available * (counts[cluster] / rem_total)
            if share > max_share:
                assigned[cluster] = max_share
                available -= max_share
                remaining.remove(cluster)
                changed = True
        if not changed:
            rem_total = sum(counts[c] for c in remaining)
            for cluster in remaining:
                assigned[cluster] = available * (counts[cluster] / rem_total)
            break
    return assigned


def personas_by_cluster(rows: Iterable[dict[str, str]]) -> dict[str, list[str]]:
    grouped = {cluster: [] for cluster in CLUSTER_ORDER}
    for row in rows:
        cluster = row["cluster_label"].replace(" ", "_")
        name = row["character"].replace(" ", "_")
        if cluster in grouped:
            grouped[cluster].append(name)
    return grouped


def build_matrix(counts: dict[str, int], distances: dict[str, dict[str, float]]) -> list[list[float]]:
    values = [
        distances[a][b]
        for a in CLUSTER_ORDER
        for b in CLUSTER_ORDER
        if a != b
    ]
    dmin = min(values)
    dmax = max(values)
    closeness: dict[tuple[str, str], float] = {}
    for a in CLUSTER_ORDER:
        for b in CLUSTER_ORDER:
            if a == b:
                continue
            dist = distances[a][b]
            closeness[(a, b)] = 0.5 + (1 - (dist - dmin) / (dmax - dmin)) * 3.5

    row_offdiag = {
        cluster: sum(closeness[(cluster, other)] for other in CLUSTER_ORDER if other != cluster)
        for cluster in CLUSTER_ORDER
    }
    proportions = capped_arc_proportions(counts, MAX_GROUP_ANGLE / (TAU - GROUP_PAD * len(CLUSTER_ORDER)))
    min_total = max(row_offdiag[cluster] / max(proportions[cluster], 1e-9) for cluster in CLUSTER_ORDER) + 8.0

    matrix: list[list[float]] = []
    for cluster in CLUSTER_ORDER:
        row: list[float] = []
        target_total = proportions[cluster] * min_total
        for other in CLUSTER_ORDER:
            if cluster == other:
                row.append(target_total - row_offdiag[cluster])
            else:
                row.append(closeness[(cluster, other)])
        matrix.append(row)
    return matrix


def chord_layout(matrix: list[list[float]], pad_angle: float = GROUP_PAD) -> tuple[list[Group], list[Chord], list[list[Subgroup]]]:
    n = len(matrix)
    group_sums = [sum(row) for row in matrix]
    total = sum(group_sums)
    k = (TAU - pad_angle * n) / total

    groups: list[Group] = []
    subgroups: list[list[Subgroup]] = [[None for _ in range(n)] for _ in range(n)]  # type: ignore[list-item]
    current = 0.0
    for i in range(n):
        start = current
        row = matrix[i]
        for j in range(n):
            value = row[j]
            a0 = current
            current += value * k
            subgroups[i][j] = Subgroup(i, j, a0, current, value)
        groups.append(Group(i, start, current, group_sums[i]))
        current += pad_angle

    chords: list[Chord] = []
    for i in range(n):
        for j in range(i, n):
            if i == j:
                continue
            s = subgroups[i][j]
            t = subgroups[j][i]
            if s.value <= 0 and t.value <= 0:
                continue
            if t.value > s.value:
                s, t = t, s
            chords.append(Chord(s, t))

    chords.sort(key=lambda chord: max(chord.source.value, chord.target.value), reverse=True)
    return groups, chords, subgroups


def make_cluster_label_records(groups: list[Group]) -> list[dict[str, object]]:
    """Return one record per line of each cluster label, stacked tangentially.

    Each line gets a small angular offset around the cluster's center angle so
    multi-line labels appear as parallel rows along the arc rather than
    collinear along the radial direction.
    """
    records: list[dict[str, object]] = []
    angular_spacing = CLUSTER_LINE_OFFSET / CLUSTER_LABEL_RADIUS
    for idx, group in enumerate(groups):
        cluster = CLUSTER_ORDER[idx]
        center_angle = (group.start_angle + group.end_angle) / 2
        parts = cluster.split("_")
        n = len(parts)
        for i, part in enumerate(parts):
            angular_offset = (i - (n - 1) / 2.0) * angular_spacing
            records.append(
                {
                    "cluster": cluster,
                    "text": part,
                    "angle": center_angle + angular_offset,
                    "radius": CLUSTER_LABEL_RADIUS,
                }
            )
    return records


def make_persona_records(grouped: dict[str, list[str]], groups: list[Group]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for idx, cluster in enumerate(CLUSTER_ORDER):
        personas = grouped[cluster]
        group = groups[idx]
        span = group.end_angle - group.start_angle
        step = span / max(len(personas), 1)
        label_stride = max(1, math.ceil(len(personas) / MAX_LABELS_PER_CLUSTER))
        for persona_idx, persona in enumerate(personas):
            angle = group.start_angle + step * (persona_idx + 0.5)
            records.append(
                {
                    "cluster": cluster,
                    "name": persona,
                    "angle": angle,
                    "show_label": persona_idx % label_stride == 0,
                }
            )
    return records


def render_svg(
    grouped: dict[str, list[str]],
    groups: list[Group],
    chords: list[Chord],
    counts: dict[str, int],
    parchment: bool = False,
) -> str:
    colors = PARCHMENT_COLORS if parchment else COLORS
    background = PARCHMENT_BACKGROUND if parchment else BACKGROUND
    text_color = PARCHMENT_TEXT if parchment else TEXT_COLOR
    persona_records = make_persona_records(grouped, groups)

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<defs>",
        '<filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="1.5" stdDeviation="2.2" flood-color="#000000" flood-opacity="0.12"/>'
        "</filter>",
        "</defs>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{background}"/>',
    ]

    for chord in chords:
        cluster = CLUSTER_ORDER[chord.source.index]
        lines.append(
            f'<path d="{ribbon_path(chord.source, chord.target, RIBBON_RADIUS)}" '
            f'fill="{rgba(colors[cluster], ribbon_alpha(cluster, parchment))}" '
            'stroke="none"/>'
        )

    lines.append(f'<circle cx="{CX}" cy="{CY}" r="{CENTER_CLEAR_RADIUS}" fill="{background}"/>')

    for idx, group in enumerate(groups):
        cluster = CLUSTER_ORDER[idx]
        lines.append(
            f'<path d="{arc_path(group.start_angle, group.end_angle, OUTER_RADIUS, ARC_INNER_RADIUS)}" '
            f'fill="{colors[cluster]}" stroke="{background}" stroke-width="2.5" filter="url(#softShadow)"/>'
        )

    for record in persona_records:
        angle = float(record["angle"])
        cluster = str(record["cluster"])
        px, py = polar(OUTER_RADIUS + 7, angle)
        lines.append(
            f'<circle cx="{px:.3f}" cy="{py:.3f}" r="{DOT_RADIUS}" fill="{PERSONA_DOT}" stroke="{colors[cluster]}" stroke-width="0.8"/>'
        )

    for record in make_cluster_label_records(groups):
        cluster = str(record["cluster"])
        angle = float(record["angle"])
        radius = float(record["radius"])
        text = str(record["text"])
        x, y, deg, anchor = text_transform(angle, radius)
        lines.append(
            f'<text x="{x:.3f}" y="{y:.3f}" transform="rotate({deg:.3f} {x:.3f} {y:.3f})" '
            f'text-anchor="{anchor}" dominant-baseline="middle" font-family="Source Sans Pro, Helvetica, Arial, sans-serif" '
            f'font-size="15" font-weight="700" fill="{colors[cluster]}">{text}</text>'
        )

    for record in persona_records:
        angle = float(record["angle"])
        cluster = str(record["cluster"])
        name = str(record["name"]).replace("_", " ")
        x, y, deg, anchor = text_transform(angle, LABEL_RADIUS)
        lines.append(
            f'<text x="{x:.3f}" y="{y:.3f}" transform="rotate({deg:.3f} {x:.3f} {y:.3f})" '
            f'text-anchor="{anchor}" dominant-baseline="middle" font-family="Source Sans Pro, Helvetica, Arial, sans-serif" '
            f'font-size="7.2" fill="{text_color}" fill-opacity="0.88">{name}</text>'
        )

    lines.append(
        f'<text x="{CX}" y="{TITLE_Y}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="Source Sans Pro, Helvetica, Arial, sans-serif" font-size="22" font-weight="700" '
        f'fill="{text_color}" fill-opacity="0.95">{TITLE_TEXT}</text>'
    )
    lines.append(
        f'<text x="{CX}" y="{SUBTITLE_Y}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="Source Sans Pro, Helvetica, Arial, sans-serif" font-size="13" '
        f'fill="{text_color}" fill-opacity="0.72">{SUBTITLE_TEXT}</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines)


def html_template(data_json: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Persona Chord Diagram</title>
  <style>
    :root {{
      --bg: #ffffff;
      --text: #5b6270;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Source Sans Pro", Helvetica, Arial, sans-serif;
    }}
    svg {{
      display: block;
      width: 1200px;
      height: 1200px;
      margin: 0 auto;
      background: var(--bg);
    }}
    .persona-label {{
      font-size: 7.2px;
      fill: var(--text);
      fill-opacity: 0.88;
    }}
    .cluster-label {{
      font-size: 15px;
      font-weight: 700;
    }}
    .title {{
      font-size: 22px;
      font-weight: 700;
      fill: var(--text);
      fill-opacity: 0.95;
    }}
    .subtitle {{
      font-size: 13px;
      fill: var(--text);
      fill-opacity: 0.72;
    }}
  </style>
</head>
<body>
<svg id="chart" viewBox="0 0 1200 1200" aria-label="Persona connectome chord diagram"></svg>
<script>
const DATA = {data_json};
const WIDTH = 1200;
const HEIGHT = 1200;
const CX = WIDTH / 2;
const CY = HEIGHT / 2;
const OUTER_RADIUS = {OUTER_RADIUS};
const ARC_INNER_RADIUS = {ARC_INNER_RADIUS};
const RIBBON_RADIUS = {RIBBON_RADIUS};
const CENTER_CLEAR_RADIUS = {CENTER_CLEAR_RADIUS};
const LABEL_RADIUS = {LABEL_RADIUS};
const CLUSTER_LABEL_RADIUS = {CLUSTER_LABEL_RADIUS};
const DOT_RADIUS = 2.0;

function polar(radius, angle) {{
  return [CX + radius * Math.cos(angle - Math.PI / 2), CY + radius * Math.sin(angle - Math.PI / 2)];
}}

const d3 = {{
  chord() {{
    let padAngle = 0;
    function layout(matrix) {{
      const n = matrix.length;
      const groupSums = matrix.map(row => row.reduce((a, b) => a + b, 0));
      const total = groupSums.reduce((a, b) => a + b, 0);
      const k = (Math.PI * 2 - padAngle * n) / total;
      let current = 0;
      const groups = [];
      const subgroups = Array.from({{ length: n }}, () => Array(n));
      for (let i = 0; i < n; i++) {{
        const start = current;
        for (let j = 0; j < n; j++) {{
          const value = matrix[i][j];
          const a0 = current;
          current += value * k;
          subgroups[i][j] = {{
            index: i,
            subindex: j,
            startAngle: a0,
            endAngle: current,
            value
          }};
        }}
        groups.push({{ index: i, startAngle: start, endAngle: current, value: groupSums[i] }});
        current += padAngle;
      }}
      const chords = [];
      for (let i = 0; i < n; i++) {{
        for (let j = i; j < n; j++) {{
          if (i === j) continue;
          let source = subgroups[i][j];
          let target = subgroups[j][i];
          if (source.value <= 0 && target.value <= 0) continue;
          if (target.value > source.value) {{
            const tmp = source;
            source = target;
            target = tmp;
          }}
          chords.push({{ source, target }});
        }}
      }}
      chords.sort((a, b) => Math.max(b.source.value, b.target.value) - Math.max(a.source.value, a.target.value));
      chords.groups = groups;
      return chords;
    }}
    layout.padAngle = function(value) {{
      if (value === undefined) return padAngle;
      padAngle = value;
      return layout;
    }};
    return layout;
  }},
  ribbon() {{
    let radius = 420;
    function path(chord) {{
      const sa0 = polar(radius, chord.source.startAngle);
      const sa1 = polar(radius, chord.source.endAngle);
      const ta0 = polar(radius, chord.target.startAngle);
      const ta1 = polar(radius, chord.target.endAngle);
      const sourceLarge = (chord.source.endAngle - chord.source.startAngle) > Math.PI ? 1 : 0;
      const targetLarge = (chord.target.endAngle - chord.target.startAngle) > Math.PI ? 1 : 0;
      return [
        `M ${{sa0[0].toFixed(3)}} ${{sa0[1].toFixed(3)}}`,
        `A ${{radius}} ${{radius}} 0 ${{sourceLarge}} 1 ${{sa1[0].toFixed(3)}} ${{sa1[1].toFixed(3)}}`,
        `Q ${{CX.toFixed(3)}} ${{CY.toFixed(3)}} ${{ta0[0].toFixed(3)}} ${{ta0[1].toFixed(3)}}`,
        `A ${{radius}} ${{radius}} 0 ${{targetLarge}} 1 ${{ta1[0].toFixed(3)}} ${{ta1[1].toFixed(3)}}`,
        `Q ${{CX.toFixed(3)}} ${{CY.toFixed(3)}} ${{sa0[0].toFixed(3)}} ${{sa0[1].toFixed(3)}} Z`
      ].join(" ");
    }}
    path.radius = function(value) {{
      if (value === undefined) return radius;
      radius = value;
      return path;
    }};
    return path;
  }}
}};

function arcPath(startAngle, endAngle, outerRadius, innerRadius) {{
  const startOuter = polar(outerRadius, startAngle);
  const endOuter = polar(outerRadius, endAngle);
  const endInner = polar(innerRadius, endAngle);
  const startInner = polar(innerRadius, startAngle);
  const largeArc = (endAngle - startAngle) > Math.PI ? 1 : 0;
  return [
    `M ${{startOuter[0].toFixed(3)}} ${{startOuter[1].toFixed(3)}}`,
    `A ${{outerRadius}} ${{outerRadius}} 0 ${{largeArc}} 1 ${{endOuter[0].toFixed(3)}} ${{endOuter[1].toFixed(3)}}`,
    `L ${{endInner[0].toFixed(3)}} ${{endInner[1].toFixed(3)}}`,
    `A ${{innerRadius}} ${{innerRadius}} 0 ${{largeArc}} 0 ${{startInner[0].toFixed(3)}} ${{startInner[1].toFixed(3)}} Z`
  ].join(" ");
}}

function textTransform(angle, radius) {{
  const [x, y] = polar(radius, angle);
  let deg = (angle - Math.PI / 2) * 180 / Math.PI;
  let anchor = "start";
  if (angle > Math.PI / 2 && angle < 3 * Math.PI / 2) {{
    deg += 180;
    anchor = "end";
  }}
  return {{ x, y, deg, anchor }};
}}

const svg = document.getElementById("chart");
svg.innerHTML = `
  <defs>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="2.2" flood-color="#000000" flood-opacity="0.12"></feDropShadow>
    </filter>
  </defs>
  <rect width="1200" height="1200" fill="#ffffff"></rect>
`;

const chords = d3.chord().padAngle(DATA.groupPad)(DATA.matrix);
const ribbon = d3.ribbon().radius(RIBBON_RADIUS);

for (const chord of chords) {{
  const cluster = DATA.clusterOrder[chord.source.index];
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", ribbon(chord));
  path.setAttribute("fill", DATA.ribbonColors[cluster]);
  path.setAttribute("stroke", "none");
  svg.appendChild(path);
}}

const clearCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
clearCircle.setAttribute("cx", CX);
clearCircle.setAttribute("cy", CY);
clearCircle.setAttribute("r", CENTER_CLEAR_RADIUS);
clearCircle.setAttribute("fill", "#ffffff");
svg.appendChild(clearCircle);

for (const group of chords.groups) {{
  const cluster = DATA.clusterOrder[group.index];
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", arcPath(group.startAngle, group.endAngle, OUTER_RADIUS, ARC_INNER_RADIUS));
  path.setAttribute("fill", DATA.colors[cluster]);
  path.setAttribute("stroke", "#ffffff");
  path.setAttribute("stroke-width", "2.5");
  path.setAttribute("filter", "url(#softShadow)");
  svg.appendChild(path);
}}

for (const persona of DATA.personas) {{
  const [px, py] = polar(OUTER_RADIUS + 7, persona.angle);
  const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  dot.setAttribute("cx", px.toFixed(3));
  dot.setAttribute("cy", py.toFixed(3));
  dot.setAttribute("r", DOT_RADIUS);
  dot.setAttribute("fill", "{PERSONA_DOT}");
  dot.setAttribute("stroke", DATA.colors[persona.cluster]);
  dot.setAttribute("stroke-width", "0.8");
  svg.appendChild(dot);
}}

const CLUSTER_LINE_OFFSET = {CLUSTER_LINE_OFFSET};
const ANGULAR_LINE_SPACING = CLUSTER_LINE_OFFSET / CLUSTER_LABEL_RADIUS;
for (const group of chords.groups) {{
  const cluster = DATA.clusterOrder[group.index];
  const centerAngle = (group.startAngle + group.endAngle) / 2;
  const parts = cluster.split("_");
  parts.forEach((part, i) => {{
    const angle = centerAngle + (i - (parts.length - 1) / 2) * ANGULAR_LINE_SPACING;
    const t = textTransform(angle, CLUSTER_LABEL_RADIUS);
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", t.x.toFixed(3));
    label.setAttribute("y", t.y.toFixed(3));
    label.setAttribute("transform", `rotate(${{t.deg.toFixed(3)}} ${{t.x.toFixed(3)}} ${{t.y.toFixed(3)}})`);
    label.setAttribute("text-anchor", t.anchor);
    label.setAttribute("dominant-baseline", "middle");
    label.setAttribute("class", "cluster-label");
    label.setAttribute("fill", DATA.colors[cluster]);
    label.textContent = part;
    svg.appendChild(label);
  }});
}}

for (const persona of DATA.personas) {{
  if (!persona.show_label) continue;
  const t = textTransform(persona.angle, LABEL_RADIUS);
  const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
  label.setAttribute("x", t.x.toFixed(3));
  label.setAttribute("y", t.y.toFixed(3));
  label.setAttribute("transform", `rotate(${{t.deg.toFixed(3)}} ${{t.x.toFixed(3)}} ${{t.y.toFixed(3)}})`);
  label.setAttribute("text-anchor", t.anchor);
  label.setAttribute("dominant-baseline", "middle");
  label.setAttribute("class", "persona-label");
  label.textContent = persona.name.replaceAll("_", " ");
  svg.appendChild(label);
}}

const titleEl = document.createElementNS("http://www.w3.org/2000/svg", "text");
titleEl.setAttribute("x", CX);
titleEl.setAttribute("y", {TITLE_Y});
titleEl.setAttribute("text-anchor", "middle");
titleEl.setAttribute("dominant-baseline", "middle");
titleEl.setAttribute("class", "title");
titleEl.textContent = "{TITLE_TEXT}";
svg.appendChild(titleEl);

const subtitle = document.createElementNS("http://www.w3.org/2000/svg", "text");
subtitle.setAttribute("x", CX);
subtitle.setAttribute("y", {SUBTITLE_Y});
subtitle.setAttribute("text-anchor", "middle");
subtitle.setAttribute("dominant-baseline", "middle");
subtitle.setAttribute("class", "subtitle");
subtitle.textContent = "{SUBTITLE_TEXT}";
svg.appendChild(subtitle);
</script>
</body>
</html>
"""


def sample_arc_points(start_angle: float, end_angle: float, radius: float, steps: int = 28) -> list[tuple[float, float]]:
    if steps < 2:
        steps = 2
    return [polar(radius, start_angle + (end_angle - start_angle) * i / (steps - 1)) for i in range(steps)]


def sample_quadratic(p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], steps: int = 24) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for i in range(steps):
        t = i / (steps - 1)
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
        out.append((x, y))
    return out


def render_png(
    grouped: dict[str, list[str]],
    groups: list[Group],
    chords: list[Chord],
    png_path: Path,
    parchment: bool = False,
) -> bool:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.colors import to_rgba
        from matplotlib.patches import Circle, Polygon
    except Exception:
        return False

    colors = PARCHMENT_COLORS if parchment else COLORS
    background = PARCHMENT_BACKGROUND if parchment else BACKGROUND
    text_color = PARCHMENT_TEXT if parchment else TEXT_COLOR
    persona_records = make_persona_records(grouped, groups)

    fig = plt.figure(figsize=(8, 8), dpi=150)
    fig.patch.set_facecolor(background)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(HEIGHT, 0)
    ax.set_aspect("equal")
    ax.set_facecolor(background)
    ax.axis("off")

    for chord in chords:
        cluster = CLUSTER_ORDER[chord.source.index]
        points = []
        points.extend(sample_arc_points(chord.source.start_angle, chord.source.end_angle, RIBBON_RADIUS, 18))
        points.extend(sample_quadratic(points[-1], (CX, CY), polar(RIBBON_RADIUS, chord.target.start_angle), 18)[1:])
        points.extend(sample_arc_points(chord.target.start_angle, chord.target.end_angle, RIBBON_RADIUS, 18)[1:])
        points.extend(sample_quadratic(points[-1], (CX, CY), polar(RIBBON_RADIUS, chord.source.start_angle), 18)[1:])
        ax.add_patch(
            Polygon(
                points,
                closed=True,
                facecolor=to_rgba(colors[cluster], ribbon_alpha(cluster, parchment)),
                edgecolor="none",
                zorder=1,
            )
        )

    ax.add_patch(Circle((CX, CY), CENTER_CLEAR_RADIUS, facecolor=background, edgecolor="none", zorder=2))

    for idx, group in enumerate(groups):
        cluster = CLUSTER_ORDER[idx]
        outer = sample_arc_points(group.start_angle, group.end_angle, OUTER_RADIUS, 42)
        inner = list(reversed(sample_arc_points(group.start_angle, group.end_angle, ARC_INNER_RADIUS, 42)))
        ax.add_patch(
            Polygon(
                outer + inner,
                closed=True,
                facecolor=colors[cluster],
                edgecolor=background,
                linewidth=2.0,
                zorder=3,
            )
        )

    for record in persona_records:
        angle = float(record["angle"])
        cluster = str(record["cluster"])
        px, py = polar(OUTER_RADIUS + 7, angle)
        ax.add_patch(Circle((px, py), DOT_RADIUS, facecolor=PERSONA_DOT, edgecolor=colors[cluster], linewidth=0.8, zorder=4))

    for record in make_cluster_label_records(groups):
        cluster = str(record["cluster"])
        angle = float(record["angle"])
        radius = float(record["radius"])
        text = str(record["text"])
        x, y, deg, anchor = text_transform(angle, radius)
        ax.text(
            x,
            y,
            text,
            rotation=deg,
            rotation_mode="anchor",
            ha=mpl_anchor(anchor),
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color=colors[cluster],
            family="DejaVu Sans",
            zorder=5,
        )

    for record in persona_records:
        if not bool(record["show_label"]):
            continue
        angle = float(record["angle"])
        name = str(record["name"]).replace("_", " ")
        x, y, deg, anchor = text_transform(angle, LABEL_RADIUS)
        ax.text(
            x,
            y,
            name,
            rotation=deg,
            rotation_mode="anchor",
            ha=mpl_anchor(anchor),
            va="center",
            fontsize=5.4,
            color=text_color,
            family="DejaVu Sans",
            alpha=0.9,
            zorder=5,
        )

    ax.text(
        CX,
        TITLE_Y,
        TITLE_TEXT,
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color=text_color,
        alpha=0.95,
        family="DejaVu Sans",
        zorder=5,
    )
    ax.text(
        CX,
        SUBTITLE_Y,
        SUBTITLE_TEXT,
        ha="center",
        va="center",
        fontsize=9,
        color=text_color,
        alpha=0.72,
        family="DejaVu Sans",
        zorder=5,
    )

    fig.savefig(png_path, dpi=150, facecolor=background)
    plt.close(fig)
    return png_path.exists()


def main() -> None:
    ranking_rows = load_full_ranking()
    grouped = personas_by_cluster(ranking_rows)
    counts = {cluster: len(grouped[cluster]) for cluster in CLUSTER_ORDER}
    distances = load_cluster_distances()
    matrix = build_matrix(counts, distances)
    groups, chords, _ = chord_layout(matrix, GROUP_PAD)
    personas = make_persona_records(grouped, groups)

    data = {
        "clusterOrder": CLUSTER_ORDER,
        "counts": counts,
        "colors": COLORS,
        "ribbonColors": {cluster: rgba(COLORS[cluster], 0.30) for cluster in CLUSTER_ORDER},
        "matrix": matrix,
        "groupPad": GROUP_PAD,
        "personas": personas,
    }

    html_path = OUT_DIR / "chord-diagram.html"
    svg_path = OUT_DIR / "chord-diagram.svg"
    png_path = OUT_DIR / "chord-diagram.png"
    parchment_svg_path = OUT_DIR / "chord-diagram-parchment.svg"
    parchment_png_path = OUT_DIR / "chord-diagram-parchment.png"

    html_path.write_text(html_template(json.dumps(data, indent=2)), encoding="utf-8")
    svg_path.write_text(render_svg(grouped, groups, chords, counts, parchment=False), encoding="utf-8")
    parchment_svg_path.write_text(render_svg(grouped, groups, chords, counts, parchment=True), encoding="utf-8")

    academic_ok = render_png(grouped, groups, chords, png_path, parchment=False)
    parchment_ok = render_png(grouped, groups, chords, parchment_png_path, parchment=True)

    print("Chord diagram exports complete.")
    print(f"HTML: {html_path}")
    print(f"SVG: {svg_path}")
    print(f"PNG: {png_path} ({'ok' if academic_ok else 'failed'})")
    print(f"Parchment SVG: {parchment_svg_path}")
    print(f"Parchment PNG: {parchment_png_path} ({'ok' if parchment_ok else 'failed'})")


if __name__ == "__main__":
    main()
