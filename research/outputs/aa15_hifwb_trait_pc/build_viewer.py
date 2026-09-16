#!/usr/bin/env python3
"""Minimally fork AA-14's deployed shell and bundled Plotly viewer after extraction."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AA14 = HERE.parent / "three_model_trait_pca"
SOURCE = AA14 / "trait_pc_persona_viewer.html"
TARGET = HERE / "hifwb_trait_pc_viewer.html"


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    assert count == 1, f"AA-14 shell changed: expected one anchor, found {count}: {old[:80]!r}"
    return source.replace(old, new, 1)


def main() -> None:
    data = json.loads((HERE / "viewer_data.json").read_text())
    assert data["version"] == "aa15-v1-prospective-analogue"
    assert all(len(m["indicators_by_form"]["primary_positive_pole"]) == 13
               for m in data["models"].values())
    html = SOURCE.read_text()
    html = replace_once(html, "<title>Trait PC Landscapes | Qwen, Llama, Gemma</title>",
                        "<title>HiFWB in Trait PC Space | Qwen, Llama, Gemma</title>")
    html = replace_once(html, "Persona geometry / <span id=\"active-model-name\">Qwen</span> / trait PCs",
                        "Persona geometry / <span id=\"active-model-name\">Qwen</span> / HiFWB trait PCs")
    html = replace_once(html, "Personas projected onto principal components fitted only to traits.",
                        "Personas and HiFWB indicators projected onto principal components fitted only to traits.")
    html = replace_once(html, "<strong>275</strong> personas<br>240 trait landmarks",
                        "<strong>275</strong> personas<br>240 traits · 13 HiFWB indicators")
    old_layer = ('<label class="control">Layers <select id="layer-select"><option value="personas">Personas only</option>'
                 '<option value="traits">Traits only</option><option value="both" selected>Personas and traits</option></select></label>')
    new_layer = ('<label class="control">Layers <select id="layer-select">'
                 '<option value="personas">Personas only</option><option value="traits">Traits only</option>'
                 '<option value="indicators">HiFWB only</option><option value="personas+traits">Personas and traits</option>'
                 '<option value="personas+indicators">Personas and HiFWB</option>'
                 '<option value="traits+indicators">Traits and HiFWB</option>'
                 '<option value="personas+traits+indicators" selected>All three layers</option></select></label>'
                 '<label class="control">Prompt <select id="formulation-select">'
                 '<option value="primary_positive_pole">Positive pole · primary</option>'
                 '<option value="exact_survey">Exact survey wording</option>'
                 '<option value="minimal_first_person">First-person wording</option></select></label>'
                 '<label class="control">Wellbeing color <select id="wellbeing-color">'
                 '<option value="population">Population</option><option value="domain">Indicator domain</option>'
                 '<option value="proximity">Persona proximity</option><option value="alignment">Direction alignment</option>'
                 '</select></label>'
                 '<label class="control">HiFWB labels <input id="indicator-labels" type="checkbox"></label>'
                 '<label class="control">Centroid <input id="centroid-toggle" type="checkbox"></label>'
                 '<label class="control">Direction ray <input id="ray-toggle" type="checkbox"></label>')
    html = replace_once(html, old_layer, new_layer)
    html = replace_once(html, '<label>Trait search <input id="trait-search" type="search" placeholder="Find a trait"></label>',
                        '<label>Trait search <input id="trait-search" type="search" placeholder="Find a trait"></label>'
                        '<label>HiFWB search <input id="indicator-search" type="search" placeholder="Find an item"></label>')
    html = replace_once(html, '<span><i class="trait-dot"></i> Trait landmarks</span>',
                        '<span><i class="trait-dot"></i> Trait landmarks</span>'
                        '<span><i class="hifwb-dot"></i> HiFWB indicators</span>')
    html = replace_once(html, '</style>',
                        '.hifwb-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#f4d572}'
                        '#selected-nearest{max-width:165px}.control input[type=checkbox]{width:15px;height:15px}'
                        '</style>')
    html = replace_once(html,
                        "PCA uses only each model's 240 trait vectors. Personas are centered using the frozen trait mean before projection. Different models have separate activation spaces.",
                        "PCA uses only each model's 240 trait contrasts. Personas and prospectively extracted HiFWB contrasts are centered using the frozen trait mean and projected afterward. HiFWB extraction is an analogue, not a method-matched historical replication. Different models have separate activation spaces.")
    html = replace_once(html,
                        "Trait vectors—not personas—are the observations in each model's PCA. Each persona is projected afterward into that model's frozen trait-derived axes.",
                        "Trait vectors—not personas or HiFWB indicators—are the observations in each model's PCA. Each persona and HiFWB indicator is projected afterward into that model's frozen trait-derived axes.")
    html = replace_once(html, '<a href="methodology_report.md">Methods and findings</a>',
                        '<a href="hifwb_trait_pc_report.md">AA-15 methods and findings</a> · '
                        '<a href="aa14_extraction_provenance_erratum.md">AA-14 provenance erratum</a>')
    html = replace_once(html, 'href="projected_personas.csv"',
                        'href="../three_model_trait_pca/projected_personas.csv"')
    html = replace_once(html, 'href="trait_pc_scores.csv"',
                        'href="../three_model_trait_pca/trait_pc_scores.csv"')
    html = replace_once(html, '<a href="../three_model_trait_pca/projected_personas.csv" download>Persona projections</a>',
                        '<a href="hifwb_projection_coordinates.csv" download>HiFWB projections</a> · '
                        '<a href="../three_model_trait_pca/projected_personas.csv" download>Persona projections</a>')
    html = replace_once(html, '<script id="viewer-data" type="application/json">' +
                        (AA14 / "viewer_data.json").read_text().strip().replace("</script>", "<\\/script>") + '</script>',
                        '<script id="viewer-data" type="application/json">' +
                        json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</script>", "<\\/script>") + '</script>')
    original_js = (AA14 / "viewer.js").read_text()
    html = replace_once(html, '<script>' + original_js + '</script>',
                        '<script>' + (HERE / "viewer.js").read_text() + '</script>')
    TARGET.write_text(html)
    print(f"Built {TARGET} from unchanged AA-14 shell ({len(html):,} chars)")


if __name__ == "__main__":
    main()
